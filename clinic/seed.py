"""Populate the database with a realistic, fully synthetic practice.

Names, accounts, and clinical content are deterministic. Dates are generated
relative to the moment the seed runs, so "today's schedule" always has
patients in it.
"""

import datetime
import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone

from audit.models import AuditLog

from . import seed_content as C
from .models import (
    Allergy,
    Appointment,
    AppointmentRequest,
    AppointmentType,
    InsurancePlan,
    LabResult,
    Medication,
    Message,
    MessageThread,
    Office,
    OfficeHours,
    Patient,
    PolicyDocument,
    Problem,
    Provider,
    ProviderSchedule,
    Specialty,
    Visit,
)
from .services import available_slots

RANDOM_SEED = 4490
MORNING = (datetime.time(8, 0), datetime.time(12, 0))
AFTERNOON = (datetime.time(13, 0), datetime.time(17, 0))
SATURDAY_BLOCKS = {
    "rachel-kimball": ("sugar-house", datetime.time(8, 0), datetime.time(12, 0)),
    "megan-holloway": ("sandy", datetime.time(9, 0), datetime.time(13, 0)),
    "olivia-grant": ("sandy", datetime.time(9, 0), datetime.time(13, 0)),
}

User = get_user_model()


def username_for(first, last):
    return f"{first}.{last}".lower().replace(" ", "").replace("'", "")


def reset_database():
    """Delete all practice data, audit history, and user accounts."""
    with transaction.atomic():
        for model in (
            AuditLog,
            Message,
            MessageThread,
            AppointmentRequest,
            Visit,
            LabResult,
            Appointment,
            Medication,
            Problem,
            Allergy,
            Patient,
            ProviderSchedule,
            Provider,
            AppointmentType,
            OfficeHours,
            PolicyDocument,
            InsurancePlan,
            Specialty,
        ):
            model.objects.all().delete()
        User.objects.all().delete()
        Office.objects.all().delete()


class Seeder:
    def __init__(self, now=None, log=None):
        self.now = now or timezone.now()
        self.today = timezone.localtime(self.now).date()
        self.rng = random.Random(RANDOM_SEED)
        self.log = log or (lambda message: None)
        self.password_hashes = {role: make_password(pw) for role, pw in C.PASSWORDS.items()}
        self.used_starts = {}  # provider_id -> [(start, end)] for generated history

    # ------------------------------------------------------------------ run
    def run(self):
        with transaction.atomic():
            self.create_directory()
            self.create_staff_accounts()
            self.create_policies()
            self.create_patients()
            self.create_clinical_history()
            self.create_current_schedule()
            self.create_appointment_requests()
            self.create_message_threads()
        return self.summary()

    def summary(self):
        return {
            "offices": Office.objects.count(),
            "providers": Provider.objects.count(),
            "patients": Patient.objects.count(),
            "patient_accounts": User.objects.filter(role=User.Role.PATIENT).count(),
            "front_office_accounts": User.objects.filter(role=User.Role.FRONT_OFFICE).count(),
            "doctor_accounts": User.objects.filter(role=User.Role.DOCTOR).count(),
            "ai_engineer_accounts": User.objects.filter(role=User.Role.AI_ENGINEER).count(),
            "appointments": Appointment.objects.count(),
            "visits": Visit.objects.count(),
            "lab_results": LabResult.objects.count(),
            "appointment_requests": AppointmentRequest.objects.count(),
            "message_threads": MessageThread.objects.count(),
            "policy_documents": PolicyDocument.objects.count(),
        }

    # -------------------------------------------------------------- helpers
    def make_user(self, *, first, last, role, password_key, email_domain="alderwickhealth.example", **extra):
        username = username_for(first, last)
        user = User(
            username=username,
            first_name=first,
            last_name=last,
            email=f"{username}@{email_domain}",
            role=role,
            **extra,
        )
        user.password = self.password_hashes[password_key]
        user.save()
        return user

    def aware(self, day, time_of_day):
        return timezone.make_aware(datetime.datetime.combine(day, time_of_day), timezone.get_current_timezone())

    # ------------------------------------------------------------ directory
    def create_directory(self):
        self.specialties = {}
        for slug, name, description in C.SPECIALTIES:
            self.specialties[slug] = Specialty.objects.create(slug=slug, name=name, description=description)

        self.plans = {}
        for code, name, carrier, plan_type, phone in C.INSURANCE_PLANS:
            self.plans[code] = InsurancePlan.objects.create(
                code=code, name=name, carrier=carrier, plan_type=plan_type, member_services_phone=phone
            )

        self.offices = {}
        for data in C.OFFICES:
            data = dict(data)
            hours = data.pop("hours")
            office = Office.objects.create(**data)
            for weekday, (opens, closes) in hours.items():
                OfficeHours.objects.create(
                    office=office,
                    weekday=weekday,
                    opens=datetime.time.fromisoformat(opens),
                    closes=datetime.time.fromisoformat(closes),
                )
            self.offices[office.slug] = office

        self.appointment_types = {}
        for code, name, minutes, description, telehealth in C.APPOINTMENT_TYPES:
            self.appointment_types[code] = AppointmentType.objects.create(
                code=code, name=name, duration_minutes=minutes, description=description, is_telehealth=telehealth
            )

        self.providers = {}
        for index, row in enumerate(C.PROVIDERS):
            (first, last, credentials, specialty, gender, languages, office_slugs, telehealth, accepting,
             since, board, education) = row
            slug = f"{first}-{last}".lower()
            user = self.make_user(
                first=first,
                last=last,
                role=User.Role.DOCTOR,
                password_key="doctor",
                job_title=f"{C.TITLES[specialty]} ({credentials})",
            )
            physician = credentials in ("MD", "DO")
            title = {
                "family-medicine": "Family Medicine Physician" if physician else "Family Medicine Clinician",
                "pediatrics": "Pediatrician" if physician else "Pediatric Nurse Practitioner",
                "internal-medicine": "Internal Medicine Physician" if physician else "Adult-Gerontology Nurse Practitioner",
                "dermatology": "Dermatologist" if physician else "Dermatology Physician Assistant",
                "sports-medicine": "Sports Medicine Physician",
                "womens-health": "Obstetrician-Gynecologist" if physician else (
                    "Certified Nurse-Midwife" if credentials == "CNM" else "Women's Health Nurse Practitioner"
                ),
            }[specialty]
            pronoun = "She" if gender == "F" else "He"
            bio = (
                f"{first} {last}, {credentials}, has cared for patients since {since}. "
                f"{pronoun} focuses on {C.BIO_FOCUS[specialty]}. "
                f"{pronoun} sees patients at {self._office_phrase(office_slugs)}"
                f"{' and offers video visits' if telehealth else ''}."
            )
            provider = Provider.objects.create(
                user=user,
                first_name=first,
                last_name=last,
                credentials=credentials,
                slug=slug,
                title=title,
                specialty=self.specialties[specialty],
                gender=gender,
                languages=languages,
                accepting_new_patients=accepting,
                offers_telehealth=telehealth,
                bio=bio,
                education=education,
                board_certification=board,
                practicing_since=since,
            )
            provider.offices.set([self.offices[s] for s in office_slugs])
            plan_codes = set(C.SPECIALTY_PLAN_RULES[specialty]) | set(C.PROVIDER_EXTRA_PLANS.get(slug, []))
            provider.insurance_plans.set([self.plans[c] for c in plan_codes])
            self._create_schedule(provider, index, office_slugs)
            self.providers[last] = provider
        self.log(f"Created {len(self.providers)} providers at {len(self.offices)} locations.")

    def _office_phrase(self, office_slugs):
        names = [
            self.offices[s].name.replace("Alderwick ", "our ").replace(" Clinic", " clinic")
            for s in office_slugs
            if not self.offices[s].is_virtual
        ]
        return " and ".join(names) if names else "Alderwick Virtual Care"

    def _create_schedule(self, provider, index, office_slugs):
        day_off = index % 5
        working_days = [d for d in range(5) if d != day_off]
        for position, weekday in enumerate(working_days):
            office = self.offices[office_slugs[position % len(office_slugs)]]
            for start, end in (MORNING, AFTERNOON):
                ProviderSchedule.objects.create(
                    provider=provider, office=office, weekday=weekday, start_time=start, end_time=end
                )
        if provider.slug in SATURDAY_BLOCKS:
            office_slug, start, end = SATURDAY_BLOCKS[provider.slug]
            ProviderSchedule.objects.create(
                provider=provider, office=self.offices[office_slug], weekday=5, start_time=start, end_time=end
            )

    # ---------------------------------------------------------------- staff
    def create_staff_accounts(self):
        self.front_office = {}
        for first, last, office_slug, job_title in C.FRONT_OFFICE_STAFF:
            user = self.make_user(
                first=first,
                last=last,
                role=User.Role.FRONT_OFFICE,
                password_key="front_office",
                job_title=job_title,
                office=self.offices[office_slug],
            )
            self.front_office.setdefault(office_slug, []).append(user)
        for first, last, job_title in C.AI_ENGINEERS:
            self.make_user(
                first=first, last=last, role=User.Role.AI_ENGINEER, password_key="ai_engineer", job_title=job_title
            )
        admin = User(
            username="admin",
            first_name="Practice",
            last_name="Administrator",
            email="admin@alderwickhealth.example",
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        admin.password = self.password_hashes["admin"]
        admin.save()

    def create_policies(self):
        effective = self.today.replace(month=1, day=1)
        for order, doc in enumerate(C.POLICY_DOCUMENTS):
            PolicyDocument.objects.create(effective_date=effective, display_order=order, **doc)

    # ------------------------------------------------------------- patients
    def create_patients(self):
        self.patients = []
        for index, row in enumerate(C.ALL_PATIENTS):
            (first, last, sex, dob, lang, plan_code, pcp_last, conditions, allergies, specialist, preferred) = row
            dob = C.parse_date(dob)
            pcp = self.providers[pcp_last]
            primary_office = pcp.offices.filter(is_virtual=False).first()
            city, postal = self.rng.choice(C.CITIES)
            contact_first, relationship = self.rng.choice(C.EMERGENCY_CONTACT_NAMES)
            age = self.today.year - dob.year - ((self.today.month, self.today.day) < (dob.month, dob.day))
            minor = age < 18
            guardian = f"{contact_first} {last}" if minor else ""
            plan = self.plans[plan_code]
            patient = Patient.objects.create(
                mrn=f"AFH{(104729 + index * 7919) % 1000000:06d}",
                first_name=first,
                last_name=last,
                preferred_name=preferred,
                date_of_birth=dob,
                sex=sex,
                phone=f"(385) 555-{100 + index:04d}",
                email=f"{username_for(contact_first if minor else first, last)}@example.com",
                address_line=f"{self.rng.randint(120, 9800)} {self.rng.choice(C.STREETS)}",
                city=city,
                postal_code=postal,
                preferred_language=C.LANGUAGES[lang],
                insurance_plan=plan,
                insurance_member_id="" if plan.plan_type == "SELF" else f"{plan.code[:3].upper()}{self.rng.randint(10**7, 10**8 - 1)}",
                primary_provider=pcp,
                primary_office=primary_office,
                guardian_name=guardian,
                emergency_contact_name=guardian or f"{contact_first} {last}",
                emergency_contact_relationship="Parent" if minor else relationship,
                emergency_contact_phone=f"(435) 555-{100 + index:04d}",
                created_at=self.now - datetime.timedelta(days=self.rng.randint(400, 3000)),
            )
            if not minor:
                patient.user = self.make_user(
                    first=first,
                    last=last,
                    role=User.Role.PATIENT,
                    password_key="patient",
                    email_domain="example.com",
                )
                patient.save(update_fields=["user"])
            patient._conditions = conditions
            patient._allergies = allergies
            patient._specialist = self.providers[specialist] if specialist else None
            self.patients.append(patient)
        self.log(f"Created {len(self.patients)} patients.")

    # ------------------------------------------------------ clinical history
    def create_clinical_history(self):
        for patient in self.patients:
            self._create_problems_meds_allergies(patient)
            self._create_past_visits(patient)
        self._create_past_no_shows()

    def _create_problems_meds_allergies(self, patient):
        for key in patient._allergies:
            substance, reaction, severity = C.ALLERGIES[key]
            Allergy.objects.create(
                patient=patient,
                substance=substance,
                reaction=reaction,
                severity=severity,
                recorded_on=self.today - datetime.timedelta(days=self.rng.randint(200, 2500)),
            )
        for key in patient._conditions:
            cond = C.CONDITIONS[key]
            if cond["chronic"]:
                onset = self.today - datetime.timedelta(days=self.rng.randint(365, 365 * 8))
                status, resolved = Problem.Status.ACTIVE, None
            elif key in ("lbp", "ankle_sprain"):
                onset = self.today - datetime.timedelta(days=self.rng.randint(180, 420))
                status, resolved = Problem.Status.RESOLVED, onset + datetime.timedelta(days=42)
            else:
                onset = self.today - datetime.timedelta(days=self.rng.randint(30, 120))
                status, resolved = Problem.Status.ACTIVE, None
            age_days = (self.today - patient.date_of_birth).days
            onset = max(onset, patient.date_of_birth + datetime.timedelta(days=min(age_days // 2, 365 * 3)))
            Problem.objects.create(
                patient=patient,
                description=cond["description"],
                icd10_code=cond["icd10"],
                status=status,
                onset_date=onset,
                resolved_date=resolved,
            )
            prescriber = self._provider_for_condition(patient, key)
            for name, dose, frequency in cond["meds"]:
                Medication.objects.create(
                    patient=patient,
                    name=name,
                    dose=dose,
                    frequency=frequency,
                    route="Topical" if any(w in name.lower() for w in ("cream", "ointment")) else (
                        "Inhaled" if "hfa" in name.lower() else "Oral"
                    ),
                    prescriber=prescriber,
                    start_date=onset,
                    is_active=status == Problem.Status.ACTIVE,
                    end_date=resolved,
                )

    def _provider_for_condition(self, patient, key):
        specialist = patient._specialist
        if specialist is not None:
            if key in C.DERMATOLOGY_CONDITIONS and specialist.specialty.slug == "dermatology":
                return specialist
            if key in C.SPORTS_CONDITIONS and specialist.specialty.slug == "sports-medicine":
                return specialist
        return patient.primary_provider

    def _history_slot(self, provider, target_day):
        """Find a past start time on or before ``target_day`` when the provider was working."""
        blocks = list(provider.schedule_blocks.select_related("office"))
        for back in range(0, 21):
            day = target_day - datetime.timedelta(days=back)
            todays = [b for b in blocks if b.weekday == day.weekday()]
            if not todays:
                continue
            block = self.rng.choice(todays)
            minutes = int(
                (datetime.datetime.combine(day, block.end_time) - datetime.datetime.combine(day, block.start_time)).seconds
                // 60
            )
            for _ in range(10):
                offset = self.rng.randrange(0, minutes - 40 + 1, 20)
                start = self.aware(day, block.start_time) + datetime.timedelta(minutes=offset)
                end = start + datetime.timedelta(minutes=40)  # long enough for any visit type
                busy = self.used_starts.setdefault(provider.pk, [])
                if start < self.now and not any(s < end and e > start for s, e in busy):
                    busy.append((start, end))
                    return block.office, start
        return None, None

    def _create_past_visits(self, patient):
        age = patient.age(self.today)
        chronic = [k for k in patient._conditions if C.CONDITIONS[k]["chronic"]]
        acute = [k for k in patient._conditions if not C.CONDITIONS[k]["chronic"]]
        plan = []  # (days_ago, kind, provider, focus conditions)
        pcp = patient.primary_provider

        if "prenatal" in patient._conditions:
            for days_ago in (12, 40, 68):
                plan.append((days_ago, "prenatal", pcp, ["prenatal"]))
        else:
            annual = "well_child" if age < 18 else "annual"
            plan.append((self.rng.randint(25, 320), annual, pcp, chronic))
            plan.append((365 + self.rng.randint(0, 40), annual, pcp, chronic))
            for key in chronic[:2]:
                if key in C.DERMATOLOGY_CONDITIONS and patient._specialist:
                    continue
                plan.append((self.rng.randint(45, 230), "follow_up", pcp, [key]))
        for key in acute + [k for k in chronic if k in C.DERMATOLOGY_CONDITIONS]:
            if key == "prenatal":
                continue
            provider = self._provider_for_condition(patient, key)
            kind = "skin_check" if key in C.DERMATOLOGY_CONDITIONS else (
                "sports" if key in C.SPORTS_CONDITIONS and provider.specialty.slug == "sports-medicine" else "sick"
            )
            days_ago = self.rng.randint(14, 110)
            problem = patient.problems.filter(icd10_code=C.CONDITIONS[key]["icd10"]).first()
            if problem and problem.status == Problem.Status.RESOLVED:
                days_ago = (self.today - problem.onset_date).days
            plan.append((days_ago, kind, provider, [key]))

        for days_ago, kind, provider, focus in plan:
            office, start = self._history_slot(provider, self.today - datetime.timedelta(days=days_ago))
            if start is None:
                continue
            self._create_completed_visit(patient, provider, office, start, kind, focus)

    VISIT_KINDS = {
        "annual": ("annual-physical", "Annual physical", "Annual preventive visit"),
        "well_child": ("well-child", "Well-child visit", "Well-child checkup"),
        "follow_up": ("follow-up", "Follow-up visit", "Chronic condition follow-up"),
        "sick": ("sick-visit", "Sick visit", None),
        "skin_check": ("skin-check", "Dermatology visit", None),
        "sports": ("follow-up", "Sports medicine evaluation", None),
        "prenatal": ("prenatal", "Prenatal visit", "Routine prenatal visit"),
    }

    def _create_completed_visit(self, patient, provider, office, start, kind, focus, status=Visit.Status.SIGNED):
        type_code, visit_type, complaint = self.VISIT_KINDS[kind]
        if office.is_virtual:
            type_code, visit_type = "telehealth", f"Video visit - {visit_type.lower()}"
        appointment_type = self.appointment_types[type_code]
        end = start + datetime.timedelta(minutes=appointment_type.duration_minutes)
        conditions = [C.CONDITIONS[k] for k in focus]
        if complaint is None:
            complaint = conditions[0]["description"] if conditions else "Acute concern"
        appointment = Appointment.objects.create(
            patient=patient,
            provider=provider,
            office=office,
            appointment_type=appointment_type,
            start=start,
            end=end,
            status=Appointment.Status.COMPLETED,
            reason=complaint,
            checked_in_at=start - datetime.timedelta(minutes=12),
            created_at=start - datetime.timedelta(days=self.rng.randint(3, 40)),
        )
        visit = Visit(
            patient=patient,
            provider=provider,
            office=office,
            appointment=appointment,
            visit_date=start,
            visit_type=visit_type,
            chief_complaint=complaint,
            created_at=start,
            **self._vitals(patient, focus, office.is_virtual),
        )
        self._write_note(visit, patient, kind, focus)
        if status == Visit.Status.SIGNED:
            visit.status = Visit.Status.SIGNED
            visit.signed_by = provider.user
            visit.signed_at = start + datetime.timedelta(hours=self.rng.randint(1, 6))
        else:
            visit.assessment = ""
            visit.plan = ""
            visit.patient_instructions = ""
        visit.save()
        if status == Visit.Status.SIGNED:
            self._create_labs(patient, provider, start.date() if timezone.is_naive(start) else timezone.localtime(start).date(), kind, focus)
        return visit

    def _vitals(self, patient, focus, virtual):
        if virtual:
            return {}
        rng = self.rng
        age = patient.age(self.today)
        if age < 18:
            weight = Decimal(str(round(18 + age * 6.2 + rng.uniform(-4, 6), 1)))
            height = Decimal(str(round(30 + age * 2.4 + rng.uniform(-1.5, 1.5), 1)))
            systolic, diastolic, hr = rng.randint(96, 112), rng.randint(56, 70), rng.randint(78, 108)
        else:
            if patient.sex == "M":
                weight, height = rng.uniform(158, 236), rng.uniform(65.5, 74)
            else:
                weight, height = rng.uniform(122, 198), rng.uniform(60.5, 68)
            weight, height = Decimal(str(round(weight, 1))), Decimal(str(round(height, 1)))
            if "htn" in patient._conditions:
                systolic, diastolic = rng.randint(124, 148), rng.randint(76, 94)
            else:
                systolic, diastolic = rng.randint(106, 128), rng.randint(64, 82)
            hr = rng.randint(58, 90)
        return {
            "blood_pressure": f"{systolic}/{diastolic}",
            "heart_rate": hr,
            "temperature_f": Decimal(str(round(rng.uniform(97.6, 98.9), 1))),
            "weight_lb": weight,
            "height_in": height,
            "oxygen_saturation": rng.randint(96, 99),
        }

    def _write_note(self, visit, patient, kind, focus):
        conditions = [(k, C.CONDITIONS[k]) for k in focus]
        pronoun = "She" if patient.sex == "F" else "He"
        name = patient.preferred_name or patient.first_name
        age = patient.age(timezone.localtime(visit.visit_date).date())
        sex_word = "female" if patient.sex == "F" else "male"

        if kind == "annual":
            subjective = [f"{age}-year-old {sex_word} here for annual preventive visit."]
        elif kind == "well_child":
            subjective = [f"{age}-year-old here with {patient.guardian_name or 'parent'} for well-child visit. Eating and sleeping well, doing well in school."]
        elif kind == "prenatal":
            subjective = [f"{age}-year-old here for routine prenatal visit."]
        else:
            subjective = [f"{age}-year-old {sex_word} presenting for {visit.chief_complaint.lower()}."]
        subjective += [c["subjective"] for _, c in conditions]
        if kind in ("annual", "well_child"):
            subjective.append("Denies chest pain, shortness of breath, abdominal pain, or new concerns.")
        visit.subjective = " ".join(subjective)

        if visit.blood_pressure:
            objective = [
                f"Vitals: BP {visit.blood_pressure}, HR {visit.heart_rate}, Temp {visit.temperature_f} F, "
                f"Wt {visit.weight_lb} lb, SpO2 {visit.oxygen_saturation}%.",
                "General: well-appearing, no acute distress.",
            ]
        else:
            objective = ["Video visit. Patient appears well, speaking in full sentences, no visible distress."]
        if kind in ("annual", "well_child", "follow_up", "prenatal"):
            objective += ["Heart: regular rate and rhythm, no murmurs.", "Lungs: clear to auscultation bilaterally."]
        if kind == "skin_check":
            objective.append("Skin: findings as described in assessment; no ulcerated or rapidly changing lesions.")
        if kind == "sports":
            objective.append("Musculoskeletal: focal tenderness as noted, full strength, neurovascularly intact distally.")
        visit.objective = "\n".join(objective)

        assessment, plan = [], []
        if kind == "annual":
            assessment.append("Encounter for routine adult health examination (Z00.00).")
            plan.append("Age-appropriate screening reviewed and updated. Return in 12 months.")
        if kind == "well_child":
            assessment.append("Encounter for routine child health examination (Z00.129).")
            plan.append("Growth and development appropriate. Immunizations up to date. Return in 12 months.")
        for _, cond in conditions:
            assessment.append(f"{cond['description']} ({cond['icd10']}): {cond['assessment']}")
            plan.append(cond["plan"])
        visit.assessment = "\n".join(f"{i}. {line}" for i, line in enumerate(assessment, start=1))
        visit.plan = "\n".join(f"- {line}" for line in plan)
        visit.patient_instructions = (
            f"Thank you for visiting Alderwick Family Health, {name}. "
            + " ".join(cond["plan"] for _, cond in conditions[:2])
            + (" Please schedule your next annual visit in 12 months." if kind in ("annual", "well_child") else "")
            + " Send us a portal message if you have questions."
        )

    def _create_labs(self, patient, provider, collected, kind, focus):
        panels = set()
        if kind == "annual" and patient.age(self.today) >= 18:
            panels.update({"cbc", "bmp"})
            if patient.age(self.today) >= 40:
                panels.add("lipid")
        for key in focus:
            panels.update(C.CONDITIONS[key]["labs"])
        if kind in ("well_child", "skin_check", "sports", "sick"):
            panels = {p for p in panels if p in C.CONDITIONS.get(focus[0], {}).get("labs", [])} if focus else set()
        for panel_key in sorted(panels):
            panel_name, tests = C.LAB_PANELS[panel_key]
            for test, unit, low, high, typ_low, typ_high, decimals, ref in tests:
                for condition in patient._conditions:
                    override = C.LAB_CONDITION_RANGES.get(condition, {}).get(test)
                    if override:
                        typ_low, typ_high = override
                raw = self.rng.uniform(typ_low, typ_high)
                value = round(raw, decimals) if decimals else int(round(raw))
                if value < low:
                    flag = LabResult.Flag.LOW
                elif value > high:
                    flag = LabResult.Flag.HIGH
                else:
                    flag = LabResult.Flag.NORMAL
                LabResult.objects.create(
                    patient=patient,
                    ordered_by=provider,
                    panel=panel_name,
                    test_name=test,
                    value=str(value),
                    unit=unit,
                    reference_range=ref,
                    flag=flag,
                    collected_on=collected,
                    resulted_on=collected + datetime.timedelta(days=1),
                )

    def _create_past_no_shows(self):
        candidates = self.rng.sample(self.patients, 6)
        for patient in candidates:
            provider = patient.primary_provider
            office, start = self._history_slot(
                provider, self.today - datetime.timedelta(days=self.rng.randint(20, 150))
            )
            if start is None:
                continue
            appointment_type = self.appointment_types["telehealth" if office.is_virtual else "follow-up"]
            Appointment.objects.create(
                patient=patient,
                provider=provider,
                office=office,
                appointment_type=appointment_type,
                start=start,
                end=start + datetime.timedelta(minutes=appointment_type.duration_minutes),
                status=Appointment.Status.NO_SHOW,
                reason="Follow-up",
                created_at=start - datetime.timedelta(days=14),
            )

    # ---------------------------------------------------- today and upcoming
    CONDITION_REASONS = {
        "htn": "Blood pressure check",
        "t2dm": "Diabetes follow-up",
        "prediabetes": "Lab review",
        "hld": "Cholesterol follow-up",
        "hypothyroid": "Thyroid follow-up",
        "anxiety": "Mood follow-up",
        "depression": "Mood follow-up",
        "asthma": "Asthma follow-up",
        "gerd": "Heartburn follow-up",
        "migraine": "Headache follow-up",
        "osteoporosis": "Bone health follow-up",
        "adhd": "ADHD medication check",
        "allergic_rhinitis": "Allergy symptoms",
        "pcos": "PCOS follow-up",
        "knee_oa": "Knee pain",
    }
    SPECIALTY_REASONS = {
        "dermatology": ["Skin check", "Rash", "Mole evaluation", "Acne follow-up"],
        "sports-medicine": ["Knee pain", "Ankle injury", "Shoulder pain", "Heel pain"],
        "pediatrics": ["Cough and congestion", "Ear pain", "Fever", "Rash"],
        "womens-health": ["Annual well-woman exam", "Contraception follow-up", "Pelvic pain"],
    }
    ACUTE_REASONS = ["Cough and congestion", "Sore throat", "Fatigue", "Medication check", "Lab review"]

    def _fits(self, provider, patient):
        """Would this patient plausibly be seen by this provider?"""
        age = patient.age(self.today)
        slug = provider.specialty.slug
        if slug == "pediatrics":
            fits = age < 18
        elif slug == "womens-health":
            fits = age >= 16 and patient.sex == "F"
        elif slug == "internal-medicine":
            fits = age >= 18
        elif slug == "sports-medicine":
            fits = age >= 12
        else:
            fits = True
        return fits and provider.accepts(patient.insurance_plan)

    def _patients_for(self, provider):
        pool = [p for p in self.patients if p.primary_provider == provider or p._specialist == provider]
        if len(pool) < 8:
            extras = [p for p in self.patients if p not in pool and self._fits(provider, p)]
            self.rng.shuffle(extras)
            pool += extras[: 8 - len(pool)]
        return pool

    def _type_for(self, provider, office, patient):
        if office.is_virtual:
            return self.appointment_types["telehealth"]
        slug = provider.specialty.slug
        if slug == "dermatology":
            return self.appointment_types["skin-check"]
        if slug == "womens-health" and "prenatal" in patient._conditions:
            return self.appointment_types["prenatal"]
        return self.appointment_types[self.rng.choice(["follow-up", "follow-up", "sick-visit"])]

    def _reason_for(self, provider, patient, appointment_type):
        """Return (reason, focus condition keys) that fit the provider and patient."""
        if appointment_type.code == "prenatal":
            return "Routine prenatal visit", ["prenatal"]
        slug = provider.specialty.slug
        own = [k for k in patient._conditions if self._provider_for_condition(patient, k) == provider]
        if slug in ("dermatology", "sports-medicine"):
            matching = [k for k in own if k in C.DERMATOLOGY_CONDITIONS | C.SPORTS_CONDITIONS]
            if matching:
                return C.CONDITIONS[matching[0]]["description"].split(",")[0], matching[:1]
            return self.rng.choice(self.SPECIALTY_REASONS[slug]), []
        chronic = [k for k in own if k in self.CONDITION_REASONS]
        if chronic and self.rng.random() < 0.75:
            key = self.rng.choice(chronic)
            return self.CONDITION_REASONS[key], [key]
        choices = self.SPECIALTY_REASONS.get(slug, self.ACUTE_REASONS)
        return self.rng.choice(choices), []

    def _patient_is_free(self, patient, start, end):
        return not any(s < end and e > start for s, e in self.patient_busy.get(patient.pk, []))

    def _book_seed_appointment(self, patient, provider, slot, **fields):
        appointment_type = self._type_for(provider, slot.office, patient)
        end = slot.start + datetime.timedelta(minutes=appointment_type.duration_minutes)
        if not self._patient_is_free(patient, slot.start, end):
            return None
        if Appointment.objects.filter(
            provider=provider, status__in=Appointment.BLOCKING_STATUSES, start__lt=end, end__gt=slot.start
        ).exists():
            return None
        reason, focus = self._reason_for(provider, patient, appointment_type)
        if appointment_type.code in ("follow-up", "sick-visit"):
            # Chronic-condition visits are follow-ups; new concerns are sick visits.
            appointment_type = self.appointment_types["follow-up" if focus else "sick-visit"]
            end = slot.start + datetime.timedelta(minutes=appointment_type.duration_minutes)
        appointment = Appointment.objects.create(
            patient=patient,
            provider=provider,
            office=slot.office,
            appointment_type=appointment_type,
            start=slot.start,
            end=end,
            reason=reason,
            **fields,
        )
        self.patient_busy.setdefault(patient.pk, []).append((slot.start, end))
        appointment._focus = focus
        return appointment

    def create_current_schedule(self):
        start_of_day = self.aware(self.today, datetime.time.min)
        self.patient_busy = {}
        seen_today = set()

        # Today's clinic: each patient appears at most once.
        for provider in self.providers.values():
            pool = self._patients_for(provider)
            slots = available_slots(provider, self.today, days=1, now=start_of_day)
            if not pool or not slots:
                continue
            chosen = sorted(self.rng.sample(slots, min(len(slots), self.rng.randint(5, 8))), key=lambda s: s.start)
            for slot in chosen:
                candidates = [p for p in pool if p.pk not in seen_today]
                if not candidates:
                    break
                patient = self.rng.choice(candidates)
                appointment = self._book_seed_appointment(
                    patient, provider, slot, created_at=self.now - datetime.timedelta(days=self.rng.randint(1, 30))
                )
                if appointment is None:
                    continue
                seen_today.add(patient.pk)
                self._progress_todays_appointment(appointment)

        # The next 30 days
        for patient in self.patients:
            for _ in range(self.rng.choice([1, 1, 2])):
                provider = patient._specialist if patient._specialist and self.rng.random() < 0.4 else patient.primary_provider
                offset = self.rng.randint(1, 30)
                slots = available_slots(provider, self.today + datetime.timedelta(days=offset), days=4, now=self.now)
                if not slots:
                    continue
                slot = self.rng.choice(slots[:12])
                cancelled = self.rng.random() < 0.08
                self._book_seed_appointment(
                    patient,
                    provider,
                    slot,
                    status=Appointment.Status.CANCELLED if cancelled else Appointment.Status.SCHEDULED,
                    cancellation_reason="Patient called to cancel" if cancelled else "",
                    created_at=self.now - datetime.timedelta(days=self.rng.randint(1, 20)),
                )

    def _progress_todays_appointment(self, appointment):
        """Move earlier appointments along: completed with a note, or checked in."""
        start = appointment.start
        if start < self.now - datetime.timedelta(minutes=60):
            appointment.status = Appointment.Status.COMPLETED
            appointment.checked_in_at = start - datetime.timedelta(minutes=10)
            appointment.save()
            patient, provider = appointment.patient, appointment.provider
            visit = Visit(
                patient=patient,
                provider=provider,
                office=appointment.office,
                appointment=appointment,
                visit_date=start,
                visit_type=appointment.appointment_type.name,
                chief_complaint=appointment.reason,
                created_at=start,
                **self._vitals(patient, appointment._focus, appointment.office.is_virtual),
            )
            kind = "prenatal" if appointment._focus == ["prenatal"] else "follow_up"
            self._write_note(visit, patient, kind, appointment._focus)
            if start < self.now - datetime.timedelta(hours=3):
                # Notes from early in the day are already signed.
                visit.status = Visit.Status.SIGNED
                visit.signed_by = provider.user
                visit.signed_at = start + datetime.timedelta(minutes=50)
            else:
                visit.assessment = ""
                visit.plan = ""
                visit.patient_instructions = ""
            visit.save()
        elif start < self.now:
            appointment.status = Appointment.Status.CHECKED_IN
            appointment.checked_in_at = start - datetime.timedelta(minutes=8)
            appointment.save()

    # ------------------------------------------------------ front office data
    def _staff_for(self, office):
        slug = office.slug if office else "sugar-house"
        return self.front_office.get(slug, self.front_office["sugar-house"])[0]

    def create_appointment_requests(self):
        for entry in C.APPOINTMENT_REQUESTS:
            created = self.now - datetime.timedelta(hours=entry["hours_ago"])
            specialty = self.specialties.get(entry.get("specialty"))
            provider = self.providers.get(entry["provider"]) if entry.get("provider") else None
            office = self.offices.get(entry["office"]) if entry.get("office") else None
            if "patient" in entry:
                patient = self.patients[entry["patient"]]
                fields = {
                    "patient": patient,
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "date_of_birth": patient.date_of_birth,
                    "email": patient.email,
                    "phone": patient.phone,
                    "is_new_patient": False,
                    "insurance_plan": patient.insurance_plan,
                }
                source = entry.get("source", "portal")
            else:
                first, last, dob, email, phone, plan_code = entry["prospect"]
                patient = None
                fields = {
                    "first_name": first,
                    "last_name": last,
                    "date_of_birth": C.parse_date(dob),
                    "email": email,
                    "phone": phone,
                    "is_new_patient": True,
                    "insurance_plan": self.plans.get(plan_code) if plan_code else None,
                    "insurance_other": entry.get("insurance_other", ""),
                }
                source = entry.get("source", "website")
            request = AppointmentRequest(
                preferred_specialty=specialty,
                preferred_provider=provider,
                preferred_office=office,
                preferred_times=entry.get("times", ""),
                reason=entry["reason"],
                source=source,
                status=entry["status"],
                staff_notes=entry.get("staff_notes", ""),
                decline_reason=entry.get("decline_reason", ""),
                created_at=created,
                **fields,
            )
            if entry["status"] != AppointmentRequest.Status.SUBMITTED:
                request.handled_by = self._staff_for(office)
            if entry["status"] == AppointmentRequest.Status.SCHEDULED:
                request.appointment = self._schedule_request(request, entry, provider, office, specialty)
                request.patient = request.appointment.patient
            request.save()
            AppointmentRequest.objects.filter(pk=request.pk).update(updated_at=created + datetime.timedelta(hours=2))

    def _schedule_request(self, request, entry, provider, office, specialty):
        patient = request.patient
        if patient is None:
            patient = Patient.objects.create(
                mrn=f"AFH{(604729 + AppointmentRequest.objects.count() * 7919) % 1000000:06d}",
                first_name=request.first_name,
                last_name=request.last_name,
                date_of_birth=request.date_of_birth,
                sex=entry.get("sex", Patient.Sex.OTHER),
                phone=request.phone,
                email=request.email,
                insurance_plan=request.insurance_plan,
                primary_provider=provider,
                primary_office=office,
                created_at=request.created_at + datetime.timedelta(hours=3),
            )
        provider = provider or specialty.providers.first()
        appointment_type = self.appointment_types[entry.get("appointment_type", "follow-up")]
        for offset in range(3, 21):
            slots = available_slots(
                provider,
                self.today + datetime.timedelta(days=offset),
                days=1,
                appointment_type=appointment_type,
                office=office,
                now=self.now,
            )
            if slots:
                slot = slots[len(slots) // 3]
                return Appointment.objects.create(
                    patient=patient,
                    provider=provider,
                    office=slot.office,
                    appointment_type=appointment_type,
                    start=slot.start,
                    end=slot.start + datetime.timedelta(minutes=appointment_type.duration_minutes),
                    reason=request.reason[:255],
                    created_by=request.handled_by,
                    created_at=request.created_at + datetime.timedelta(hours=3),
                )
        raise RuntimeError(f"No slot found to schedule request for {request.full_name}")

    def create_message_threads(self):
        for patient_index, category, subject, conversation, status in C.MESSAGE_THREADS:
            patient = self.patients[patient_index]
            first_time = self.now - datetime.timedelta(hours=conversation[0][1])
            thread = MessageThread(
                patient=patient, category=category, subject=subject, status=status, created_at=first_time
            )
            thread.route()
            thread.save()
            last_time, last_from_patient = first_time, True
            for from_patient, hours_ago, body in conversation:
                sent = self.now - datetime.timedelta(hours=hours_ago)
                if from_patient:
                    sender = patient.user
                    sender_name = patient.guardian_name if patient.guardian_name else patient.full_name
                elif thread.queue == MessageThread.Queue.CLINICAL:
                    sender = thread.assigned_provider.user
                    sender_name = thread.assigned_provider.display_name
                else:
                    sender = self._staff_for(patient.primary_office)
                    sender_name = f"{sender.first_name} {sender.last_name}, Front Office"
                Message.objects.create(
                    thread=thread,
                    sender=sender,
                    sender_name=sender_name,
                    from_patient=from_patient,
                    body=body,
                    created_at=sent,
                )
                last_time, last_from_patient = sent, from_patient
            thread.updated_at = last_time
            thread.staff_has_unread = last_from_patient and status == MessageThread.Status.OPEN
            thread.patient_has_unread = not last_from_patient and (self.now - last_time).days < 3
            thread.save()


def seed_database(now=None, log=None):
    return Seeder(now=now, log=log).run()
