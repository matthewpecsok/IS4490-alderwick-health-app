import datetime
import io
import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.management import CommandError, call_command
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from clinic import seed_content as C
from clinic.models import (
    Appointment,
    AppointmentRequest,
    MessageThread,
    Office,
    Patient,
    PolicyDocument,
    Provider,
    Visit,
)
from clinic.seed import reset_database, seed_database

SEED_NOW = timezone.make_aware(datetime.datetime(2026, 11, 4, 10, 30))  # a Wednesday morning


class SeededPracticeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.summary = seed_database(now=SEED_NOW)

    def test_directory_counts(self):
        self.assertEqual(Office.objects.count(), 5)
        self.assertEqual(Provider.objects.count(), len(C.PROVIDERS))
        self.assertEqual(PolicyDocument.objects.count(), len(C.POLICY_DOCUMENTS))
        self.assertEqual(Office.objects.filter(is_virtual=True).count(), 1)

    def test_account_counts(self):
        self.assertEqual(User.objects.filter(role=User.Role.FRONT_OFFICE).count(), 10)
        self.assertEqual(User.objects.filter(role=User.Role.DOCTOR).count(), 24)
        self.assertEqual(User.objects.filter(role=User.Role.AI_ENGINEER).count(), 2)
        self.assertTrue(User.objects.get(username="admin").is_superuser)
        adults = [p for p in C.ALL_PATIENTS if Patient.objects.get(first_name=p[0], last_name=p[1]).age(SEED_NOW.date()) >= 18]
        self.assertEqual(User.objects.filter(role=User.Role.PATIENT).count(), len(adults))

    def test_patients_have_complete_records(self):
        seeded = [f"AFH{(104729 + i * 7919) % 1000000:06d}" for i in range(len(C.ALL_PATIENTS))]
        self.assertEqual(Patient.objects.filter(mrn__in=seeded).count(), len(C.ALL_PATIENTS))
        for patient in Patient.objects.filter(mrn__in=seeded):
            with self.subTest(patient=patient.full_name):
                self.assertIsNotNone(patient.primary_provider)
                self.assertTrue(patient.visits.exists())
                if patient.age(SEED_NOW.date()) < 18:
                    self.assertIsNone(patient.user)
                    self.assertTrue(patient.guardian_name)
                else:
                    self.assertEqual(patient.user.role, User.Role.PATIENT)

    def test_every_doctor_account_links_to_a_provider(self):
        for user in User.objects.filter(role=User.Role.DOCTOR):
            self.assertTrue(Provider.objects.filter(user=user).exists())

    def test_documented_passwords_work_for_each_role(self):
        for username, role in [
            ("michael.anderson", "patient"),
            ("brittany.hale", "front_office"),
            ("james.whitaker", "doctor"),
            ("nikhil.rao", "ai_engineer"),
            ("admin", "admin"),
        ]:
            with self.subTest(username=username):
                self.assertIsNotNone(authenticate(username=username, password=C.PASSWORDS[role]))

    def test_user_guide_accounts_exist_with_correct_roles(self):
        guide = (Path(settings.BASE_DIR) / "USER-GUIDE.md").read_text().split("\n## Accounts\n", 1)[1]
        sections = {
            "### AI engineers": User.Role.AI_ENGINEER,
            "### Front office": User.Role.FRONT_OFFICE,
            "### Doctors and other clinicians": User.Role.DOCTOR,
            "### Patients": User.Role.PATIENT,
        }
        checked = 0
        for heading, role in sections.items():
            body = guide.split(heading, 1)[1].split("\n### ", 1)[0]
            usernames = re.findall(r"^\| [^|]+ \| `([a-z.\-]+)` \|", body, flags=re.MULTILINE)
            self.assertTrue(usernames, heading)
            for username in usernames:
                with self.subTest(username=username):
                    self.assertEqual(User.objects.get(username=username).role, role)
                    checked += 1
        self.assertEqual(checked, User.objects.exclude(role=User.Role.ADMIN).count())

    def test_no_provider_is_double_booked(self):
        for provider in Provider.objects.all():
            appointments = list(
                provider.appointments.filter(status__in=Appointment.BLOCKING_STATUSES).order_by("start")
            )
            for earlier, later in zip(appointments, appointments[1:]):
                with self.subTest(provider=provider.short_name, at=later.start):
                    self.assertLessEqual(earlier.end, later.start)

    def test_appointments_fall_inside_provider_schedule(self):
        for appointment in Appointment.objects.select_related("provider"):
            local = timezone.localtime(appointment.start)
            local_end = timezone.localtime(appointment.end)
            blocks = appointment.provider.schedule_blocks.filter(
                weekday=local.weekday(), office=appointment.office,
                start_time__lte=local.time(), end_time__gte=local_end.time(),
            )
            with self.subTest(appointment=appointment.pk):
                self.assertTrue(blocks.exists())

    def test_today_has_a_working_clinic(self):
        today = timezone.localtime(SEED_NOW).date()
        todays = Appointment.objects.filter(start__date=today)
        self.assertGreater(todays.count(), 60)
        per_patient = {}
        for appointment in todays.exclude(status=Appointment.Status.CANCELLED):
            per_patient[appointment.patient_id] = per_patient.get(appointment.patient_id, 0) + 1
        self.assertEqual(max(per_patient.values()), 1)
        self.assertTrue(todays.filter(status=Appointment.Status.SCHEDULED).exists())
        self.assertTrue(todays.filter(status__in=[Appointment.Status.CHECKED_IN, Appointment.Status.COMPLETED]).exists())

    def test_specialists_see_appropriate_patients(self):
        for appointment in Appointment.objects.select_related("patient", "provider__specialty"):
            slug = appointment.provider.specialty.slug
            age = appointment.patient.age(timezone.localtime(appointment.start).date())
            with self.subTest(appointment=appointment.pk):
                if slug == "pediatrics":
                    self.assertLess(age, 19)
                if slug == "womens-health":
                    self.assertEqual(appointment.patient.sex, "F")

    def test_generated_panel_is_deterministic(self):
        self.assertEqual(C.generate_additional_patients(), C.ALL_PATIENTS[len(C.PATIENTS):])
        self.assertEqual(len(C.ALL_PATIENTS), len(C.PATIENTS) + C.EXTRA_PATIENT_COUNT)

    def test_visit_notes(self):
        self.assertTrue(Visit.objects.filter(status=Visit.Status.DRAFT).exists())
        for visit in Visit.objects.filter(status=Visit.Status.SIGNED):
            self.assertTrue(visit.assessment and visit.plan and visit.signed_at)

    def test_message_routing(self):
        for thread in MessageThread.objects.select_related("patient"):
            with self.subTest(thread=thread.subject):
                self.assertTrue(thread.messages.exists())
                if thread.queue == MessageThread.Queue.CLINICAL:
                    self.assertEqual(thread.assigned_provider, thread.patient.primary_provider)
                else:
                    self.assertIsNone(thread.assigned_provider)

    def test_appointment_requests(self):
        self.assertEqual(AppointmentRequest.objects.count(), len(C.APPOINTMENT_REQUESTS))
        for request in AppointmentRequest.objects.filter(status=AppointmentRequest.Status.SCHEDULED):
            self.assertIsNotNone(request.appointment)
            self.assertEqual(request.appointment.patient, request.patient)
        for request in AppointmentRequest.objects.filter(status=AppointmentRequest.Status.DECLINED):
            self.assertTrue(request.decline_reason)
        self.assertTrue(AppointmentRequest.objects.filter(status=AppointmentRequest.Status.SUBMITTED).exists())

    def test_summary_matches_database(self):
        self.assertEqual(self.summary["patients"], Patient.objects.count())
        self.assertEqual(self.summary["appointments"], Appointment.objects.count())


class SeedDeterminismTests(TestCase):
    def test_reseeding_recreates_the_same_people(self):
        seed_database(now=SEED_NOW)
        first = set(User.objects.values_list("username", flat=True))
        mrns = set(Patient.objects.values_list("mrn", flat=True))
        reset_database()
        self.assertFalse(User.objects.exists())
        self.assertFalse(Patient.objects.exists())
        seed_database(now=SEED_NOW + datetime.timedelta(days=9))
        self.assertEqual(first, set(User.objects.values_list("username", flat=True)))
        self.assertEqual(mrns, set(Patient.objects.values_list("mrn", flat=True)))


class SeedCommandTests(TestCase):
    def test_command_seeds_and_refuses_to_overwrite(self):
        out = io.StringIO()
        call_command("seed_demo_data", "--as-of", "2026-11-04T10:30", stdout=out)
        self.assertIn("Alderwick demo data loaded", out.getvalue())
        with self.assertRaises(CommandError):
            call_command("seed_demo_data", stdout=io.StringIO())
        call_command("seed_demo_data", "--reset", "--as-of", "2026-11-05T09:00", stdout=io.StringIO())
        self.assertEqual(Provider.objects.count(), len(C.PROVIDERS))

    def test_command_rejects_bad_date(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo_data", "--as-of", "next tuesday", stdout=io.StringIO())
