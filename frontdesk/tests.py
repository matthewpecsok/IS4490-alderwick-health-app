import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from audit.models import AuditLog
from clinic.models import Appointment, AppointmentRequest, MessageThread, Patient, Problem
from clinic.services import available_slots
from clinic.testing import (
    local_dt,
    make_appointment,
    make_appointment_type,
    make_patient,
    make_plan,
    make_provider,
    make_thread,
    make_user,
    tomorrow,
)


class FrontDeskTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.plan = make_plan()
        cls.provider = make_provider(plans=[cls.plan])
        cls.office = cls.provider.offices.first()
        cls.staff = make_user("front_office", office=cls.office, first_name="Brit", last_name="Hale")
        cls.patient = make_patient(provider=cls.provider, first_name="Mike", last_name="Anderson", insurance_plan=cls.plan)
        cls.type = make_appointment_type()

    def setUp(self):
        self.client.force_login(self.staff)

    def new_request(self, **kwargs):
        defaults = {
            "first_name": "Rae",
            "last_name": "Newcomer",
            "date_of_birth": datetime.date(1991, 2, 3),
            "email": "rae@example.com",
            "reason": "Physical",
            "insurance_plan": self.plan,
        }
        defaults.update(kwargs)
        return AppointmentRequest.objects.create(**defaults)

    def open_slot(self, provider=None):
        provider = provider or self.provider
        return available_slots(provider, tomorrow(), days=1, appointment_type=self.type)[0]

    def action(self, req, **data):
        return self.client.post(reverse("frontdesk:request_action", args=[req.pk]), data)


class FrontDeskAccessTests(FrontDeskTestCase):
    def test_other_roles_are_denied(self):
        for role in ("patient", "doctor", "ai_engineer"):
            with self.subTest(role=role):
                self.client.force_login(make_user(role))
                self.assertEqual(self.client.get(reverse("frontdesk:dashboard")).status_code, 403)

    def test_anonymous_redirected(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("frontdesk:dashboard")).status_code, 302)

    def test_pages_render(self):
        for name in ("dashboard", "requests", "schedule", "messages", "patient_search"):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(f"frontdesk:{name}")).status_code, 200)


class DashboardTests(FrontDeskTestCase):
    def test_counts(self):
        self.new_request()
        self.new_request(status=AppointmentRequest.Status.UNDER_REVIEW)
        make_thread(patient=self.patient, category="billing")
        start = local_dt(timezone.localdate(), 23, 0)
        make_appointment(patient=self.patient, provider=self.provider, start=start, status=Appointment.Status.CHECKED_IN)
        counts = self.client.get(reverse("frontdesk:dashboard")).context["counts"]
        self.assertEqual(counts["new_requests"], 1)
        self.assertEqual(counts["under_review"], 1)
        self.assertEqual(counts["unread_messages"], 1)
        self.assertEqual(counts["todays_appointments"], 1)
        self.assertEqual(counts["checked_in"], 1)


class RequestQueueTests(FrontDeskTestCase):
    def test_default_shows_open_requests(self):
        open_req = self.new_request()
        self.new_request(status=AppointmentRequest.Status.DECLINED)
        response = self.client.get(reverse("frontdesk:requests"))
        self.assertEqual(list(response.context["page"]), [open_req])

    def test_filters(self):
        declined = self.new_request(status=AppointmentRequest.Status.DECLINED)
        phone = self.new_request(source=AppointmentRequest.Source.PHONE, last_name="Caller")
        url = reverse("frontdesk:requests")
        self.assertEqual(list(self.client.get(url + "?status=declined").context["page"]), [declined])
        self.assertEqual(list(self.client.get(url + "?source=phone").context["page"]), [phone])
        self.assertEqual(list(self.client.get(url + "?q=caller").context["page"]), [phone])
        self.assertEqual(len(self.client.get(url + "?status=all").context["page"]), 2)

    def test_detail_shows_slots_and_insurance_warning(self):
        req = self.new_request(insurance_plan=make_plan())
        response = self.client.get(
            reverse("frontdesk:request_detail", args=[req.pk]) + f"?provider={self.provider.pk}&appointment_type={self.type.pk}"
        )
        self.assertTrue(response.context["slots_by_day"])
        self.assertTrue(response.context["insurance_warning"])

    def test_detail_suggests_matching_existing_patient(self):
        req = self.new_request(first_name="Mike", last_name="anderson", date_of_birth=self.patient.date_of_birth)
        response = self.client.get(reverse("frontdesk:request_detail", args=[req.pk]))
        self.assertIn(self.patient, list(response.context["matches"]))


class RequestActionTests(FrontDeskTestCase):
    def test_start_review_and_notes(self):
        req = self.new_request()
        self.action(req, action="start_review")
        self.action(req, action="save_notes", staff_notes="Left voicemail")
        req.refresh_from_db()
        self.assertEqual(req.status, AppointmentRequest.Status.UNDER_REVIEW)
        self.assertEqual(req.handled_by, self.staff)
        self.assertEqual(req.staff_notes, "Left voicemail")
        self.assertEqual(AuditLog.objects.filter(action=AuditLog.Action.UPDATE_APPOINTMENT_REQUEST).count(), 2)

    def test_decline_requires_reason(self):
        req = self.new_request()
        self.action(req, action="decline", decline_reason="")
        req.refresh_from_db()
        self.assertEqual(req.status, AppointmentRequest.Status.SUBMITTED)
        self.action(req, action="decline", decline_reason="We don't offer that service")
        req.refresh_from_db()
        self.assertEqual(req.status, AppointmentRequest.Status.DECLINED)
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.DECLINE_APPOINTMENT_REQUEST).exists())

    def test_closed_request_rejects_changes(self):
        req = self.new_request(status=AppointmentRequest.Status.DECLINED)
        response = self.client.post(reverse("frontdesk:request_action", args=[req.pk]), {"action": "start_review"}, follow=True)
        self.assertContains(response, "already closed")

    def test_unknown_action(self):
        req = self.new_request()
        response = self.action(req, action="explode")
        self.assertEqual(response.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, AppointmentRequest.Status.SUBMITTED)

    def test_link_existing_patient(self):
        req = self.new_request()
        self.action(req, action="link_patient", patient_id=self.patient.pk)
        req.refresh_from_db()
        self.assertEqual(req.patient, self.patient)

    def test_book_for_existing_patient(self):
        req = self.new_request(patient=self.patient, is_new_patient=False)
        slot = self.open_slot()
        self.action(req, action="book", provider=self.provider.pk, appointment_type=self.type.pk, slot=slot.value)
        req.refresh_from_db()
        self.assertEqual(req.status, AppointmentRequest.Status.SCHEDULED)
        self.assertEqual(req.appointment.start, slot.start)
        self.assertEqual(req.appointment.patient, self.patient)
        self.assertEqual(req.appointment.created_by, self.staff)
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.SCHEDULE_APPOINTMENT).exists())

    def test_book_new_patient_registers_them(self):
        req = self.new_request()
        slot = self.open_slot()
        before = Patient.objects.count()
        self.action(req, action="book", provider=self.provider.pk, appointment_type=self.type.pk, slot=slot.value, sex="F")
        self.assertEqual(Patient.objects.count(), before + 1)
        req.refresh_from_db()
        new_patient = req.patient
        self.assertEqual(new_patient.last_name, "Newcomer")
        self.assertEqual(new_patient.sex, "F")
        self.assertEqual(new_patient.primary_provider, self.provider)
        self.assertRegex(new_patient.mrn, r"^AFH\d{6}$")
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.REGISTER_PATIENT).exists())

    def test_book_rejects_missing_or_taken_slot(self):
        req = self.new_request(patient=self.patient)
        self.action(req, action="book", provider=self.provider.pk, appointment_type=self.type.pk, slot="garbage")
        req.refresh_from_db()
        self.assertEqual(req.status, AppointmentRequest.Status.SUBMITTED)

        slot = self.open_slot()
        make_appointment(patient=self.patient, provider=self.provider, start=slot.start)
        response = self.client.post(
            reverse("frontdesk:request_action", args=[req.pk]),
            {"action": "book", "provider": self.provider.pk, "appointment_type": self.type.pk, "slot": slot.value},
            follow=True,
        )
        self.assertContains(response, "no longer available")
        req.refresh_from_db()
        self.assertIsNone(req.appointment)


class ScheduleTests(FrontDeskTestCase):
    def test_filters_by_day_and_office(self):
        day = tomorrow()
        mine = make_appointment(patient=self.patient, provider=self.provider, start=local_dt(day, 9))
        elsewhere_provider = make_provider()
        make_appointment(patient=self.patient, provider=elsewhere_provider, start=local_dt(day, 9))
        response = self.client.get(reverse("frontdesk:schedule") + f"?date={day.isoformat()}")
        self.assertEqual(list(response.context["appointments"]), [mine])
        response = self.client.get(reverse("frontdesk:schedule") + f"?date={day.isoformat()}&office=")
        self.assertEqual(len(response.context["appointments"]), 2)
        bad = self.client.get(reverse("frontdesk:schedule") + "?date=not-a-date")
        self.assertEqual(bad.context["day"], timezone.localdate())

    def post_action(self, appointment, **data):
        return self.client.post(reverse("frontdesk:appointment_action", args=[appointment.pk]), data)

    def test_check_in_no_show_and_cancel(self):
        start = local_dt(tomorrow(), 9)
        a = make_appointment(patient=self.patient, provider=self.provider, start=start)
        self.post_action(a, action="check_in")
        a.refresh_from_db()
        self.assertEqual(a.status, Appointment.Status.CHECKED_IN)
        self.assertIsNotNone(a.checked_in_at)

        b = make_appointment(patient=self.patient, provider=self.provider, start=start + datetime.timedelta(hours=1))
        self.post_action(b, action="no_show")
        b.refresh_from_db()
        self.assertEqual(b.status, Appointment.Status.NO_SHOW)

        c = make_appointment(patient=self.patient, provider=self.provider, start=start + datetime.timedelta(hours=2))
        self.post_action(c, action="cancel", reason="")
        c.refresh_from_db()
        self.assertEqual(c.status, Appointment.Status.SCHEDULED)
        self.post_action(c, action="cancel", reason="Patient sick")
        c.refresh_from_db()
        self.assertEqual(c.status, Appointment.Status.CANCELLED)
        self.assertEqual(c.cancellation_reason, "Patient sick")
        actions = set(AuditLog.objects.values_list("action", flat=True))
        self.assertTrue({"check_in", "mark_no_show", "cancel_appointment"} <= actions)

    def test_invalid_transition(self):
        a = make_appointment(
            patient=self.patient, provider=self.provider, start=local_dt(tomorrow(), 9), status=Appointment.Status.CANCELLED
        )
        response = self.client.post(
            reverse("frontdesk:appointment_action", args=[a.pk]), {"action": "check_in"}, follow=True
        )
        self.assertContains(response, "isn&#x27;t available")

    def test_unsafe_next_url_is_ignored(self):
        a = make_appointment(patient=self.patient, provider=self.provider, start=local_dt(tomorrow(), 9))
        response = self.post_action(a, action="check_in", next="https://evil.example.com/")
        self.assertEqual(response["Location"], reverse("frontdesk:schedule"))
        b = make_appointment(patient=self.patient, provider=self.provider, start=local_dt(tomorrow(), 10))
        response = self.post_action(b, action="check_in", next="/staff/front-office/schedule/?date=2030-01-01")
        self.assertEqual(response["Location"], "/staff/front-office/schedule/?date=2030-01-01")


class FrontDeskMessageTests(FrontDeskTestCase):
    def test_inbox_shows_only_front_office_queue(self):
        billing = make_thread(patient=self.patient, category="billing")
        clinical = make_thread(patient=self.patient, category="clinical")
        response = self.client.get(reverse("frontdesk:messages"))
        self.assertIn(billing, response.context["page"])
        self.assertNotIn(clinical, response.context["page"])
        self.assertEqual(self.client.get(reverse("frontdesk:thread", args=[clinical.pk])).status_code, 404)

    def test_reply_and_close(self):
        thread = make_thread(patient=self.patient, category="records")
        self.client.get(reverse("frontdesk:thread", args=[thread.pk]))
        thread.refresh_from_db()
        self.assertFalse(thread.staff_has_unread)
        self.client.post(reverse("frontdesk:thread", args=[thread.pk]), {"body": "Sent!"})
        reply = thread.messages.last()
        self.assertFalse(reply.from_patient)
        self.assertEqual(reply.sender_name, "Brit Hale, Front Office")
        thread.refresh_from_db()
        self.assertTrue(thread.patient_has_unread)
        self.client.post(reverse("frontdesk:thread", args=[thread.pk]), {"action": "close"})
        thread.refresh_from_db()
        self.assertEqual(thread.status, MessageThread.Status.CLOSED)

    def test_status_filter(self):
        closed = make_thread(patient=self.patient, category="billing", status=MessageThread.Status.CLOSED)
        response = self.client.get(reverse("frontdesk:messages") + "?status=closed")
        self.assertEqual(list(response.context["page"]), [closed])


class PatientLookupTests(FrontDeskTestCase):
    def test_search_variants(self):
        url = reverse("frontdesk:patient_search")
        for query in ("anderson", self.patient.mrn, self.patient.date_of_birth.isoformat(), "Mike Anderson"):
            with self.subTest(query=query):
                self.assertIn(self.patient, list(self.client.get(url, {"q": query}).context["patients"]))
        self.assertEqual(list(self.client.get(url).context["patients"]), [])

    def test_profile_hides_clinical_data_and_is_audited(self):
        Problem.objects.create(patient=self.patient, description="Secret diagnosis", icd10_code="I10")
        response = self.client.get(reverse("frontdesk:patient_detail", args=[self.patient.pk]))
        self.assertContains(response, self.patient.mrn)
        self.assertNotContains(response, "Secret diagnosis")
        self.assertTrue(
            AuditLog.objects.filter(action=AuditLog.Action.VIEW_PATIENT_PROFILE, patient=self.patient).exists()
        )

    def test_phone_booking(self):
        url = reverse("frontdesk:book_for_patient", args=[self.patient.pk])
        page = self.client.get(url)
        self.assertEqual(page.context["picker_provider"], self.provider)
        slot = self.open_slot()
        response = self.client.post(
            url, {"provider": self.provider.pk, "appointment_type": self.type.pk, "slot": slot.value, "reason": "Cough"}
        )
        self.assertRedirects(response, reverse("frontdesk:patient_detail", args=[self.patient.pk]))
        appointment = self.patient.appointments.get()
        self.assertEqual(appointment.reason, "Cough")
        bad = self.client.post(url, {"provider": self.provider.pk, "appointment_type": self.type.pk, "slot": "x"})
        self.assertRedirects(bad, url)
