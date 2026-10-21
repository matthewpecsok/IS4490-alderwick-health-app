"""Business logic shared by the patient, front-office, and clinician views."""

import datetime
from dataclasses import dataclass

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Appointment, MessageThread, Message, Patient, Provider

SLOT_INTERVAL_MINUTES = 20


class SlotUnavailable(Exception):
    """Raised when a requested appointment time cannot be booked."""


@dataclass(frozen=True)
class Slot:
    provider: Provider
    office: object
    start: datetime.datetime
    end: datetime.datetime

    @property
    def value(self):
        """Compact form-safe identifier: '<office_id>|<ISO start>'."""
        return f"{self.office.pk}|{self.start.isoformat()}"

    @property
    def local_start(self):
        return timezone.localtime(self.start)


def _aware(day, time_of_day):
    return timezone.make_aware(datetime.datetime.combine(day, time_of_day), timezone.get_current_timezone())


def available_slots(provider, start_date, days=14, appointment_type=None, office=None, now=None, limit=None):
    """Return open appointment slots for ``provider`` in chronological order.

    Slots come from the provider's weekly schedule blocks, start every
    ``SLOT_INTERVAL_MINUTES``, are long enough for ``appointment_type``, are in
    the future relative to ``now``, and do not overlap any appointment that
    blocks the calendar.
    """
    now = now or timezone.now()
    duration = datetime.timedelta(minutes=appointment_type.duration_minutes if appointment_type else 20)
    step = datetime.timedelta(minutes=SLOT_INTERVAL_MINUTES)

    blocks = list(provider.schedule_blocks.select_related("office").order_by("start_time"))
    if office is not None:
        blocks = [b for b in blocks if b.office_id == office.pk]

    window_start = _aware(start_date, datetime.time.min)
    window_end = _aware(start_date + datetime.timedelta(days=days), datetime.time.min)
    booked = list(
        Appointment.objects.filter(
            provider=provider,
            status__in=Appointment.BLOCKING_STATUSES,
            start__lt=window_end,
            end__gt=window_start,
        ).values_list("start", "end")
    )

    slots = []
    for offset in range(days):
        day = start_date + datetime.timedelta(days=offset)
        for block in blocks:
            if block.weekday != day.weekday():
                continue
            cursor = _aware(day, block.start_time)
            block_end = _aware(day, block.end_time)
            while cursor + duration <= block_end:
                slot_end = cursor + duration
                overlaps = any(start < slot_end and end > cursor for start, end in booked)
                if cursor > now and not overlaps:
                    slots.append(Slot(provider=provider, office=block.office, start=cursor, end=slot_end))
                    if limit and len(slots) >= limit:
                        return slots
                cursor += step
    return slots


def next_available_slot(provider, now=None, days=30, appointment_type=None):
    now = now or timezone.now()
    slots = available_slots(
        provider, timezone.localtime(now).date(), days=days, appointment_type=appointment_type, now=now, limit=1
    )
    return slots[0] if slots else None


def book_appointment(*, patient, provider, office, appointment_type, start, created_by=None, reason="", now=None):
    """Create an appointment if the slot is still open. Raises ``SlotUnavailable`` otherwise."""
    now = now or timezone.now()
    end = start + datetime.timedelta(minutes=appointment_type.duration_minutes)
    local_day = timezone.localtime(start).date()
    with transaction.atomic():
        open_slots = available_slots(
            provider, local_day, days=1, appointment_type=appointment_type, office=office, now=now
        )
        if not any(slot.start == start for slot in open_slots):
            raise SlotUnavailable("That time is no longer available. Please choose another slot.")
        return Appointment.objects.create(
            patient=patient,
            provider=provider,
            office=office,
            appointment_type=appointment_type,
            start=start,
            end=end,
            reason=reason[:255],
            created_by=created_by,
        )


def parse_slot_value(value):
    """Inverse of ``Slot.value``. Returns (office_id, aware datetime) or raises ValueError."""
    office_part, _, start_part = value.partition("|")
    start = datetime.datetime.fromisoformat(start_part)
    if timezone.is_naive(start):
        raise ValueError("Slot time must include a timezone offset.")
    return int(office_part), start


# ---------------------------------------------------------------------------
# Access rules
# ---------------------------------------------------------------------------


def patients_for_provider(provider):
    """Patients a clinician has a care relationship with."""
    return (
        Patient.objects.filter(
            Q(primary_provider=provider) | Q(appointments__provider=provider) | Q(visits__provider=provider)
        )
        .distinct()
        .order_by("last_name", "first_name")
    )


def provider_can_view_patient(provider, patient):
    if provider is None or patient is None:
        return False
    return patients_for_provider(provider).filter(pk=patient.pk).exists()


# ---------------------------------------------------------------------------
# Messaging
# ---------------------------------------------------------------------------


def start_thread(*, patient, category, subject, body, sender):
    thread = MessageThread(patient=patient, category=category, subject=subject)
    thread.route()
    thread.staff_has_unread = True
    thread.patient_has_unread = False
    thread.save()
    Message.objects.create(
        thread=thread, sender=sender, sender_name=patient.full_name, from_patient=True, body=body
    )
    return thread


def reply_to_thread(*, thread, body, sender, from_patient, sender_name=None):
    now = timezone.now()
    message = Message.objects.create(
        thread=thread,
        sender=sender,
        sender_name=sender_name or (sender.display_name if sender else "Alderwick Family Health"),
        from_patient=from_patient,
        body=body,
        created_at=now,
    )
    thread.updated_at = now
    thread.status = MessageThread.Status.OPEN
    if from_patient:
        thread.staff_has_unread = True
    else:
        thread.patient_has_unread = True
        thread.staff_has_unread = False
    thread.save(update_fields=["updated_at", "status", "staff_has_unread", "patient_has_unread"])
    return message
