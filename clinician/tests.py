import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from audit.models import AuditLog
from clinic.models import Appointment, LabResult, MessageThread, Visit
from clinic.testing import (
    local_dt,
    make_appointment,
    make_patient,
    make_provider,
    make_thread,
    make_user,
    make_visit,
    tomorrow,
)


class ClinicianTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.provider = make_provider(first_name="James", last_name="Whitaker")
        cls.colleague = make_provider()
        cls.patient = make_patient(provider=cls.provider)
        cls.stranger = make_patient(provider=cls.colleague)

    def setUp(self):
        self.client.force_login(self.provider.user)


class ClinicianAccessTests(ClinicianTestCase):
    def test_other_roles_denied(self):
        for role in ("patient", "front_office", "ai_engineer"):
            with self.subTest(role=role):
                self.client.force_login(make_user(role))
                self.assertEqual(self.client.get(reverse("clinician:dashboard")).status_code, 403)

    def test_doctor_without_provider_profile_gets_404(self):
        self.client.force_login(make_user("doctor"))
        self.assertEqual(self.client.get(reverse("clinician:dashboard")).status_code, 404)

    def test_pages_render(self):
        for name in ("dashboard", "schedule", "patients", "inbox"):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(f"clinician:{name}")).status_code, 200)


class DashboardAndScheduleTests(ClinicianTestCase):
    def test_dashboard_lists_today_drafts_and_messages(self):
        today = local_dt(timezone.localdate(), 23, 0)
        appointment = make_appointment(patient=self.patient, provider=self.provider, start=today)
        draft = make_visit(patient=self.patient, provider=self.provider, status=Visit.Status.DRAFT)
        thread = make_thread(patient=self.patient, category="clinical")
        LabResult.objects.create(
            patient=self.patient, ordered_by=self.provider, test_name="LDL", value="180",
            flag=LabResult.Flag.HIGH, collected_on=timezone.localdate(),
        )
        context = self.client.get(reverse("clinician:dashboard")).context
        self.assertIn(appointment, context["todays"])
        self.assertIn(draft, context["drafts"])
        self.assertIn(thread, context["inbox"])
        self.assertEqual(context["awaiting_count"], 1)
        self.assertEqual(len(context["abnormal_labs"]), 1)

    def test_schedule_by_date(self):
        day = tomorrow()
        appointment = make_appointment(patient=self.patient, provider=self.provider, start=local_dt(day, 9))
        make_appointment(patient=self.stranger, provider=self.colleague, start=local_dt(day, 9))
        response = self.client.get(reverse("clinician:schedule") + f"?date={day.isoformat()}")
        self.assertEqual(list(response.context["appointments"]), [appointment])
        self.assertEqual(self.client.get(reverse("clinician:schedule") + "?date=bad").context["day"], timezone.localdate())


class ChartAccessTests(ClinicianTestCase):
    def test_patient_list_is_care_relationships_only(self):
        response = self.client.get(reverse("clinician:patients"))
        self.assertIn(self.patient, response.context["patients"])
        self.assertNotIn(self.stranger, response.context["patients"])
        search = self.client.get(reverse("clinician:patients") + f"?q={self.patient.last_name}")
        self.assertEqual(list(search.context["patients"]), [self.patient])

    def test_chart_is_audited(self):
        response = self.client.get(reverse("clinician:chart", args=[self.patient.pk]))
        self.assertEqual(response.status_code, 200)
        event = AuditLog.objects.get(action=AuditLog.Action.VIEW_CHART)
        self.assertEqual(event.patient, self.patient)
        self.assertEqual(event.user, self.provider.user)

    def test_chart_outside_care_relationship_is_denied_and_audited(self):
        response = self.client.get(reverse("clinician:chart", args=[self.stranger.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            AuditLog.objects.filter(action=AuditLog.Action.ACCESS_DENIED, patient=self.stranger).exists()
        )
        self.assertFalse(AuditLog.objects.filter(action=AuditLog.Action.VIEW_CHART).exists())

    def test_scheduling_creates_care_relationship(self):
        make_appointment(patient=self.stranger, provider=self.provider, start=local_dt(tomorrow(), 9))
        self.assertEqual(self.client.get(reverse("clinician:chart", args=[self.stranger.pk])).status_code, 200)

    def test_visit_detail_respects_access(self):
        mine = make_visit(patient=self.patient, provider=self.colleague)
        theirs = make_visit(patient=self.stranger, provider=self.colleague)
        response = self.client.get(reverse("clinician:visit_detail", args=[mine.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_edit"])
        self.assertEqual(self.client.get(reverse("clinician:visit_detail", args=[theirs.pk])).status_code, 403)


class NoteTests(ClinicianTestCase):
    def note_data(self, **overrides):
        data = {
            "chief_complaint": "Follow-up",
            "blood_pressure": "128/82",
            "heart_rate": "72",
            "temperature_f": "98.4",
            "weight_lb": "180",
            "height_in": "70",
            "oxygen_saturation": "98",
            "subjective": "Doing well.",
            "objective": "Normal exam.",
            "assessment": "1. Hypertension, controlled.",
            "plan": "- Continue lisinopril.",
            "patient_instructions": "Keep taking your medicine.",
        }
        data.update(overrides)
        return data

    def test_start_note_creates_one_draft_per_appointment(self):
        appointment = make_appointment(patient=self.patient, provider=self.provider, start=local_dt(tomorrow(), 9))
        first = self.client.get(reverse("clinician:start_note", args=[appointment.pk]))
        visit = Visit.objects.get(appointment=appointment)
        self.assertRedirects(first, reverse("clinician:edit_note", args=[visit.pk]))
        self.client.get(reverse("clinician:start_note", args=[appointment.pk]))
        self.assertEqual(Visit.objects.filter(appointment=appointment).count(), 1)
        self.assertEqual(visit.status, Visit.Status.DRAFT)

    def test_cannot_start_note_for_colleagues_or_cancelled_appointments(self):
        theirs = make_appointment(patient=self.stranger, provider=self.colleague, start=local_dt(tomorrow(), 9))
        self.assertEqual(self.client.get(reverse("clinician:start_note", args=[theirs.pk])).status_code, 404)
        cancelled = make_appointment(
            patient=self.patient, provider=self.provider, start=local_dt(tomorrow(), 10), status=Appointment.Status.CANCELLED
        )
        self.assertRedirects(self.client.get(reverse("clinician:start_note", args=[cancelled.pk])), reverse("clinician:schedule"))

    def test_save_draft(self):
        visit = make_visit(patient=self.patient, provider=self.provider, status=Visit.Status.DRAFT, assessment="", plan="")
        response = self.client.post(reverse("clinician:edit_note", args=[visit.pk]), self.note_data(save="1"))
        self.assertRedirects(response, reverse("clinician:edit_note", args=[visit.pk]))
        visit.refresh_from_db()
        self.assertEqual(visit.blood_pressure, "128/82")
        self.assertEqual(visit.status, Visit.Status.DRAFT)
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.SAVE_VISIT_NOTE).exists())

    def test_signing_requires_assessment_and_plan(self):
        visit = make_visit(patient=self.patient, provider=self.provider, status=Visit.Status.DRAFT)
        response = self.client.post(reverse("clinician:edit_note", args=[visit.pk]), self.note_data(plan="", sign="1"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "required before signing")
        visit.refresh_from_db()
        self.assertEqual(visit.status, Visit.Status.DRAFT)

    def test_sign_note_completes_appointment(self):
        appointment = make_appointment(
            patient=self.patient, provider=self.provider, start=local_dt(timezone.localdate(), 0, 20),
            status=Appointment.Status.CHECKED_IN,
        )
        visit = make_visit(patient=self.patient, provider=self.provider, status=Visit.Status.DRAFT, appointment=appointment)
        response = self.client.post(reverse("clinician:edit_note", args=[visit.pk]), self.note_data(sign="1"))
        self.assertRedirects(response, reverse("clinician:visit_detail", args=[visit.pk]))
        visit.refresh_from_db()
        appointment.refresh_from_db()
        self.assertTrue(visit.is_signed)
        self.assertEqual(visit.signed_by, self.provider.user)
        self.assertEqual(appointment.status, Appointment.Status.COMPLETED)
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.SIGN_VISIT_NOTE).exists())

    def test_signed_notes_are_locked(self):
        visit = make_visit(patient=self.patient, provider=self.provider)
        response = self.client.get(reverse("clinician:edit_note", args=[visit.pk]))
        self.assertRedirects(response, reverse("clinician:visit_detail", args=[visit.pk]))

    def test_cannot_edit_colleagues_note(self):
        visit = make_visit(patient=self.patient, provider=self.colleague, status=Visit.Status.DRAFT)
        self.assertEqual(self.client.get(reverse("clinician:edit_note", args=[visit.pk])).status_code, 403)

    def test_blood_pressure_format(self):
        visit = make_visit(patient=self.patient, provider=self.provider, status=Visit.Status.DRAFT)
        response = self.client.post(reverse("clinician:edit_note", args=[visit.pk]), self.note_data(blood_pressure="high"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("blood_pressure", response.context["form"].errors)


class ClinicianMessagingTests(ClinicianTestCase):
    def test_inbox_shows_assigned_clinical_threads_only(self):
        mine = make_thread(patient=self.patient, category="clinical")
        billing = make_thread(patient=self.patient, category="billing")
        theirs = make_thread(patient=self.stranger, category="clinical")
        threads = list(self.client.get(reverse("clinician:inbox")).context["threads"])
        self.assertEqual(threads, [mine])
        self.assertEqual(self.client.get(reverse("clinician:thread", args=[theirs.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("clinician:thread", args=[billing.pk])).status_code, 404)

    def test_reply_and_close(self):
        thread = make_thread(patient=self.patient, category="test_results")
        self.client.post(reverse("clinician:thread", args=[thread.pk]), {"body": "Your results look good."})
        reply = thread.messages.last()
        self.assertEqual(reply.sender_name, self.provider.display_name)
        self.assertFalse(reply.from_patient)
        self.client.post(reverse("clinician:thread", args=[thread.pk]), {"action": "close"})
        thread.refresh_from_db()
        self.assertEqual(thread.status, MessageThread.Status.CLOSED)
        closed = self.client.get(reverse("clinician:inbox") + "?status=closed").context["threads"]
        self.assertIn(thread, closed)
