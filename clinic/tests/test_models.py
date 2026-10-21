import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from clinic.models import Appointment, AppointmentRequest, LabResult, MessageThread, OfficeHours, Patient, Visit
from clinic.testing import (
    make_appointment,
    make_office,
    make_patient,
    make_plan,
    make_provider,
    make_thread,
    make_user,
    make_visit,
)


class OfficeTests(TestCase):
    def test_address_and_services(self):
        office = make_office(services="Primary care\n\nX-ray\n")
        self.assertEqual(office.full_address, "100 Test Way, Salt Lake City, UT 84101")
        self.assertEqual(office.service_list, ["Primary care", "X-ray"])
        self.assertEqual(str(office), office.name)
        self.assertEqual(office.get_absolute_url(), f"/locations/{office.slug}/")

    def test_virtual_office_address(self):
        self.assertIn("Video visits", make_office(is_virtual=True).full_address)

    def test_is_open_on(self):
        office = make_office()
        OfficeHours.objects.create(office=office, weekday=0, opens=datetime.time(8), closes=datetime.time(17))
        self.assertTrue(office.is_open_on(0))
        self.assertFalse(office.is_open_on(6))


class ProviderTests(TestCase):
    def test_physician_names(self):
        provider = make_provider(first_name="Elena", last_name="Marquez", credentials="MD")
        self.assertTrue(provider.is_physician)
        self.assertEqual(provider.display_name, "Dr. Elena Marquez, MD")
        self.assertEqual(provider.short_name, "Dr. Marquez")
        self.assertEqual(provider.initials, "EM")

    def test_non_physician_names(self):
        provider = make_provider(first_name="Rachel", last_name="Kimball", credentials="PA-C")
        self.assertFalse(provider.is_physician)
        self.assertEqual(provider.display_name, "Rachel Kimball, PA-C")
        self.assertEqual(provider.short_name, "Rachel Kimball, PA-C")

    def test_lists_and_insurance(self):
        plan, other = make_plan(), make_plan()
        provider = make_provider(languages="English, Spanish ,", education="MD, Somewhere\n\nResidency", plans=[plan])
        self.assertEqual(provider.language_list, ["English", "Spanish"])
        self.assertEqual(provider.education_list, ["MD, Somewhere", "Residency"])
        self.assertTrue(provider.accepts(plan))
        self.assertFalse(provider.accepts(other))
        self.assertFalse(provider.accepts(None))
        self.assertEqual(provider.get_absolute_url(), f"/providers/{provider.slug}/")


class PatientTests(TestCase):
    def test_age_handles_birthdays(self):
        patient = make_patient(date_of_birth=datetime.date(2000, 6, 15))
        self.assertEqual(patient.age(on=datetime.date(2026, 6, 14)), 25)
        self.assertEqual(patient.age(on=datetime.date(2026, 6, 15)), 26)

    def test_is_minor(self):
        today = timezone.localdate()
        child = make_patient(date_of_birth=today.replace(year=today.year - 10))
        adult = make_patient(date_of_birth=today.replace(year=today.year - 30))
        self.assertTrue(child.is_minor)
        self.assertFalse(adult.is_minor)

    def test_display_name_uses_preferred_name(self):
        patient = make_patient(first_name="Michael", last_name="Anderson", preferred_name="Mike")
        self.assertEqual(patient.display_name, "Michael “Mike” Anderson")
        same = make_patient(first_name="Ana", last_name="Ruiz", preferred_name="Ana")
        self.assertEqual(same.display_name, "Ana Ruiz")
        self.assertIn(same.mrn, str(same))

    def test_generate_mrn_is_unique_and_formatted(self):
        mrn = Patient.generate_mrn()
        self.assertRegex(mrn, r"^AFH\d{6}$")
        self.assertFalse(Patient.objects.filter(mrn=mrn).exists())


class AppointmentTests(TestCase):
    def setUp(self):
        self.provider = make_provider()
        self.patient = make_patient(provider=self.provider)

    def test_duration_and_upcoming(self):
        start = timezone.now() + datetime.timedelta(days=2)
        appointment = make_appointment(patient=self.patient, provider=self.provider, start=start)
        self.assertEqual(appointment.duration_minutes, 20)
        self.assertTrue(appointment.is_upcoming())
        self.assertFalse(appointment.is_upcoming(now=start + datetime.timedelta(minutes=1)))
        self.assertIn(self.patient.full_name, str(appointment))

    def test_patient_can_cancel_only_with_24_hours_notice(self):
        now = timezone.now()
        far = make_appointment(patient=self.patient, provider=self.provider, start=now + datetime.timedelta(hours=25))
        near = make_appointment(patient=self.patient, provider=self.provider, start=now + datetime.timedelta(hours=23))
        self.assertTrue(far.patient_can_cancel(now=now))
        self.assertFalse(near.patient_can_cancel(now=now))
        far.status = Appointment.Status.CANCELLED
        self.assertFalse(far.patient_can_cancel(now=now))


class VisitTests(TestCase):
    def setUp(self):
        self.provider = make_provider()
        self.patient = make_patient(provider=self.provider)

    def test_sign_sets_fields_and_cannot_repeat(self):
        visit = make_visit(patient=self.patient, provider=self.provider, status=Visit.Status.DRAFT)
        self.assertFalse(visit.is_signed)
        visit.sign(self.provider.user)
        visit.refresh_from_db()
        self.assertTrue(visit.is_signed)
        self.assertEqual(visit.signed_by, self.provider.user)
        self.assertIsNotNone(visit.signed_at)
        with self.assertRaises(ValueError):
            visit.sign(self.provider.user)

    def test_bmi(self):
        visit = make_visit(patient=self.patient, provider=self.provider, weight_lb=Decimal("180"), height_in=Decimal("70"))
        self.assertEqual(visit.bmi, 25.8)
        self.assertIsNone(make_visit(patient=self.patient, provider=self.provider).bmi)
        self.assertIn("Follow-up visit", str(visit))


class LabResultTests(TestCase):
    def test_is_abnormal(self):
        patient = make_patient()
        normal = LabResult.objects.create(patient=patient, test_name="TSH", value="2.1", collected_on=timezone.localdate())
        high = LabResult.objects.create(
            patient=patient, test_name="LDL", value="160", flag=LabResult.Flag.HIGH, collected_on=timezone.localdate()
        )
        self.assertFalse(normal.is_abnormal)
        self.assertTrue(high.is_abnormal)
        self.assertEqual(str(normal), "TSH: 2.1")


class AppointmentRequestTests(TestCase):
    def test_reference_is_generated_once(self):
        request = AppointmentRequest.objects.create(
            first_name="Ann", last_name="Lee", date_of_birth=datetime.date(1990, 1, 1), reason="Checkup"
        )
        self.assertRegex(request.reference, r"^AR-[0-9A-F]{6}$")
        original = request.reference
        request.save()
        self.assertEqual(request.reference, original)
        self.assertEqual(request.full_name, "Ann Lee")
        self.assertTrue(request.is_open)
        request.status = AppointmentRequest.Status.DECLINED
        self.assertFalse(request.is_open)


class MessageThreadTests(TestCase):
    def test_queue_for_category(self):
        self.assertEqual(MessageThread.queue_for_category("billing"), MessageThread.Queue.FRONT_OFFICE)
        self.assertEqual(MessageThread.queue_for_category("records"), MessageThread.Queue.FRONT_OFFICE)
        self.assertEqual(MessageThread.queue_for_category("prescription"), MessageThread.Queue.CLINICAL)
        self.assertEqual(MessageThread.queue_for_category("clinical"), MessageThread.Queue.CLINICAL)

    def test_route_assigns_primary_provider_for_clinical(self):
        provider = make_provider()
        patient = make_patient(provider=provider)
        clinical = make_thread(patient=patient, category=MessageThread.Category.TEST_RESULTS)
        office = make_thread(patient=patient, category=MessageThread.Category.BILLING)
        self.assertEqual(clinical.assigned_provider, provider)
        self.assertIsNone(office.assigned_provider)

    def test_awaiting_reply_and_last_message(self):
        patient = make_patient()
        thread = make_thread(patient=patient, body="First")
        self.assertEqual(thread.last_message.body, "First")
        self.assertTrue(thread.awaiting_practice_reply)
        staff = make_user("front_office")
        thread.messages.create(sender=staff, sender_name="Staff", from_patient=False, body="Reply",
                               created_at=timezone.now() + datetime.timedelta(seconds=5))
        self.assertFalse(thread.awaiting_practice_reply)


class StringRepresentationTests(TestCase):
    def test_every_model_has_a_readable_string(self):
        from clinic.models import (
            Allergy, AppointmentType, Medication, Message, PolicyDocument, Problem, ProviderSchedule,
        )

        provider = make_provider(last_name="Chen")
        patient = make_patient(provider=provider, first_name="Kenji", last_name="Watanabe")
        office = provider.offices.first()
        hours = OfficeHours.objects.create(office=office, weekday=1, opens=datetime.time(8), closes=datetime.time(17))
        thread = make_thread(patient=patient, subject="Refill", body="Please refill my medication")
        request = AppointmentRequest.objects.create(
            first_name="Ann", last_name="Lee", date_of_birth=datetime.date(1990, 1, 1), reason="x"
        )
        policy = PolicyDocument.objects.create(
            title="Video Visits", slug="video", category="visit_preparation", summary="s", body="b",
            effective_date=datetime.date(2026, 1, 1),
        )
        expectations = [
            (hours, "Tuesday 08:00-17:00"),
            (ProviderSchedule.objects.filter(provider=provider).first(), "Dr. Chen"),
            (AppointmentType.objects.create(code="sick", name="Sick visit", duration_minutes=20), "Sick visit (20 min)"),
            (Allergy.objects.create(patient=patient, substance="Latex"), "Latex (Mild)"),
            (Problem.objects.create(patient=patient, description="Hypertension", icd10_code="I10"), "Hypertension [I10]"),
            (Medication.objects.create(patient=patient, name="Lisinopril", dose="10 mg"), "Lisinopril 10 mg"),
            (request, f"{request.reference} Ann Lee"),
            (thread, "Refill (Kenji Watanabe)"),
            (thread.messages.first(), "Kenji Watanabe: Please refill my medication"),
            (policy, "Video Visits"),
        ]
        for obj, text in expectations:
            with self.subTest(model=type(obj).__name__):
                self.assertIn(text, str(obj))
        self.assertEqual(policy.get_absolute_url(), "/patient-resources/video/")
