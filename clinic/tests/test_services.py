import datetime

from django.test import TestCase

from clinic.models import Appointment, Message, MessageThread
from clinic.services import (
    SlotUnavailable,
    available_slots,
    book_appointment,
    next_available_slot,
    parse_slot_value,
    patients_for_provider,
    provider_can_view_patient,
    reply_to_thread,
    start_thread,
)
from clinic.testing import (
    local_dt,
    make_appointment,
    make_appointment_type,
    make_office,
    make_patient,
    make_provider,
    make_user,
    make_visit,
)

DAY = datetime.date(2030, 3, 4)  # a Monday
BEFORE = local_dt(DAY, 0, 1)


class AvailableSlotsTests(TestCase):
    def setUp(self):
        self.provider = make_provider(weekdays=[0], start=(8, 0), end=(10, 0))
        self.patient = make_patient(provider=self.provider)

    def starts(self, slots):
        return [s.local_start.strftime("%H:%M") for s in slots]

    def test_twenty_minute_grid_within_block(self):
        slots = available_slots(self.provider, DAY, days=1, now=BEFORE)
        self.assertEqual(self.starts(slots), ["08:00", "08:20", "08:40", "09:00", "09:20", "09:40"])
        self.assertEqual(slots[0].office, self.provider.offices.first())

    def test_longer_visits_must_fit_in_block(self):
        forty = make_appointment_type(code="new-patient", minutes=40)
        slots = available_slots(self.provider, DAY, days=1, appointment_type=forty, now=BEFORE)
        self.assertEqual(self.starts(slots)[-1], "09:20")

    def test_past_slots_are_excluded(self):
        slots = available_slots(self.provider, DAY, days=1, now=local_dt(DAY, 9, 0))
        self.assertEqual(self.starts(slots), ["09:20", "09:40"])

    def test_booked_time_is_excluded_but_cancelled_is_not(self):
        make_appointment(patient=self.patient, provider=self.provider, start=local_dt(DAY, 8, 20))
        make_appointment(
            patient=self.patient, provider=self.provider, start=local_dt(DAY, 9, 0), status=Appointment.Status.CANCELLED
        )
        slots = self.starts(available_slots(self.provider, DAY, days=1, now=BEFORE))
        self.assertNotIn("08:20", slots)
        self.assertIn("09:00", slots)

    def test_overlap_blocks_neighbouring_long_slot(self):
        make_appointment(patient=self.patient, provider=self.provider, start=local_dt(DAY, 8, 20))
        forty = make_appointment_type(code="new-patient", minutes=40)
        slots = self.starts(available_slots(self.provider, DAY, days=1, appointment_type=forty, now=BEFORE))
        self.assertNotIn("08:00", slots)
        self.assertIn("08:40", slots)

    def test_days_without_blocks_have_no_slots(self):
        tuesday = DAY + datetime.timedelta(days=1)
        self.assertEqual(available_slots(self.provider, tuesday, days=1, now=BEFORE), [])

    def test_office_filter_and_limit(self):
        other_office = make_office()
        self.assertEqual(available_slots(self.provider, DAY, days=1, office=other_office, now=BEFORE), [])
        self.assertEqual(len(available_slots(self.provider, DAY, days=7, now=BEFORE, limit=2)), 2)

    def test_next_available_slot(self):
        slot = next_available_slot(self.provider, now=BEFORE, days=7)
        self.assertEqual(slot.local_start.strftime("%Y-%m-%d %H:%M"), "2030-03-04 08:00")
        nobody = make_provider(weekdays=[])
        self.assertIsNone(next_available_slot(nobody, now=BEFORE))


class BookAppointmentTests(TestCase):
    def setUp(self):
        self.provider = make_provider(weekdays=[0], start=(8, 0), end=(10, 0))
        self.patient = make_patient(provider=self.provider)
        self.office = self.provider.offices.first()
        self.type = make_appointment_type()

    def book(self, start, **kwargs):
        return book_appointment(
            patient=self.patient,
            provider=self.provider,
            office=self.office,
            appointment_type=self.type,
            start=start,
            now=BEFORE,
            **kwargs,
        )

    def test_books_open_slot(self):
        staff = make_user("front_office")
        appointment = self.book(local_dt(DAY, 8, 40), created_by=staff, reason="x" * 300)
        self.assertEqual(appointment.end, local_dt(DAY, 9, 0))
        self.assertEqual(appointment.status, Appointment.Status.SCHEDULED)
        self.assertEqual(appointment.created_by, staff)
        self.assertEqual(len(appointment.reason), 255)

    def test_double_booking_is_rejected(self):
        self.book(local_dt(DAY, 8, 40))
        with self.assertRaises(SlotUnavailable):
            self.book(local_dt(DAY, 8, 40))

    def test_off_schedule_and_off_grid_times_are_rejected(self):
        with self.assertRaises(SlotUnavailable):
            self.book(local_dt(DAY, 12, 0))
        with self.assertRaises(SlotUnavailable):
            self.book(local_dt(DAY, 8, 10))

    def test_past_time_is_rejected(self):
        with self.assertRaises(SlotUnavailable):
            book_appointment(
                patient=self.patient,
                provider=self.provider,
                office=self.office,
                appointment_type=self.type,
                start=local_dt(DAY, 8, 0),
                now=local_dt(DAY, 9, 0),
            )


class SlotValueTests(TestCase):
    def test_round_trip(self):
        provider = make_provider(weekdays=[0])
        slot = available_slots(provider, DAY, days=1, now=BEFORE)[0]
        office_id, start = parse_slot_value(slot.value)
        self.assertEqual(office_id, slot.office.pk)
        self.assertEqual(start, slot.start)

    def test_rejects_bad_values(self):
        for bad in ["", "abc", "1|not-a-date", "1|2030-03-04T08:00:00"]:
            with self.subTest(value=bad), self.assertRaises(ValueError):
                parse_slot_value(bad)


class AccessRuleTests(TestCase):
    def test_care_relationships(self):
        provider = make_provider()
        other = make_provider()
        primary = make_patient(provider=provider)
        scheduled = make_patient(provider=other)
        seen = make_patient(provider=other)
        stranger = make_patient(provider=other)
        make_appointment(patient=scheduled, provider=provider, start=local_dt(DAY, 8, 0))
        make_appointment(patient=scheduled, provider=provider, start=local_dt(DAY, 9, 0))
        make_visit(patient=seen, provider=provider)

        panel = list(patients_for_provider(provider))
        self.assertCountEqual(panel, [primary, scheduled, seen])
        self.assertTrue(provider_can_view_patient(provider, scheduled))
        self.assertFalse(provider_can_view_patient(provider, stranger))
        self.assertFalse(provider_can_view_patient(None, stranger))
        self.assertFalse(provider_can_view_patient(provider, None))


class MessagingServiceTests(TestCase):
    def setUp(self):
        self.provider = make_provider()
        self.patient = make_patient(provider=self.provider)

    def test_start_thread_routes_and_records_first_message(self):
        thread = start_thread(
            patient=self.patient, category="clinical", subject="Rash", body="Itchy", sender=self.patient.user
        )
        self.assertEqual(thread.queue, MessageThread.Queue.CLINICAL)
        self.assertEqual(thread.assigned_provider, self.provider)
        self.assertTrue(thread.staff_has_unread)
        message = thread.messages.get()
        self.assertTrue(message.from_patient)
        self.assertEqual(message.sender_name, self.patient.full_name)

    def test_staff_reply_flags_patient_and_reopens(self):
        thread = start_thread(
            patient=self.patient, category="billing", subject="Bill", body="Why?", sender=self.patient.user
        )
        thread.status = MessageThread.Status.CLOSED
        thread.save()
        staff = make_user("front_office", first_name="Brit", last_name="Hale")
        reply_to_thread(thread=thread, body="Here's why", sender=staff, from_patient=False)
        thread.refresh_from_db()
        self.assertEqual(thread.status, MessageThread.Status.OPEN)
        self.assertTrue(thread.patient_has_unread)
        self.assertFalse(thread.staff_has_unread)
        self.assertEqual(Message.objects.filter(thread=thread).last().sender_name, "Brit Hale")

    def test_patient_reply_flags_staff(self):
        thread = start_thread(
            patient=self.patient, category="billing", subject="Bill", body="Why?", sender=self.patient.user
        )
        thread.staff_has_unread = False
        thread.save()
        reply_to_thread(thread=thread, body="Also...", sender=self.patient.user, from_patient=True, sender_name="J")
        thread.refresh_from_db()
        self.assertTrue(thread.staff_has_unread)
        self.assertEqual(thread.messages.count(), 2)
