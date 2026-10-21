"""Shared slot-picker logic for front-office scheduling screens."""

import datetime

from django.utils import timezone

from clinic.models import AppointmentType, Provider
from clinic.services import available_slots


def slot_picker_context(params, *, default_specialty=None, default_provider=None, patient_plan=None):
    providers = Provider.objects.filter(is_active=True).select_related("specialty").order_by(
        "specialty__name", "last_name"
    )
    provider = None
    if params.get("provider"):
        provider = providers.filter(pk=params.get("provider")).first()
    elif default_provider is not None:
        provider = default_provider

    appointment_types = AppointmentType.objects.all()
    appointment_type = appointment_types.filter(pk=params.get("appointment_type")).first() if params.get(
        "appointment_type"
    ) else appointment_types.filter(code="follow-up").first()

    today = timezone.localdate()
    try:
        start_date = datetime.date.fromisoformat(params.get("start", ""))
    except ValueError:
        start_date = today
    start_date = max(start_date, today)

    slots_by_day = []
    if provider is not None:
        slots = available_slots(provider, start_date, days=7, appointment_type=appointment_type)
        if appointment_type is not None:
            slots = [s for s in slots if s.office.is_virtual == appointment_type.is_telehealth]
        days = {}
        for slot in slots:
            days.setdefault(slot.local_start.date(), []).append(slot)
        slots_by_day = sorted(days.items())

    return {
        "picker_providers": providers,
        "picker_provider": provider,
        "picker_types": appointment_types,
        "picker_type": appointment_type,
        "picker_start": start_date,
        "picker_prev": max(start_date - datetime.timedelta(days=7), today),
        "picker_next": start_date + datetime.timedelta(days=7),
        "slots_by_day": slots_by_day,
        "insurance_warning": (
            provider is not None and patient_plan is not None and not provider.accepts(patient_plan)
        ),
        "default_specialty": default_specialty,
    }
