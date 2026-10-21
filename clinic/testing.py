"""Factories for building small, explicit test fixtures."""

import datetime
import itertools

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    Appointment,
    AppointmentType,
    InsurancePlan,
    MessageThread,
    Message,
    Office,
    Patient,
    Provider,
    ProviderSchedule,
    Specialty,
    Visit,
)

PASSWORD = "Test-pass-4490!"
_counter = itertools.count(1)


def _n():
    return next(_counter)


def aware(year, month, day, hour=0, minute=0):
    return timezone.make_aware(datetime.datetime(year, month, day, hour, minute), timezone.get_current_timezone())


def local_dt(day, hour, minute=0):
    return timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour, minute)), timezone.get_current_timezone())


def tomorrow():
    return timezone.localdate() + datetime.timedelta(days=1)


def make_user(role, **kwargs):
    i = _n()
    User = get_user_model()
    return User.objects.create_user(
        username=kwargs.pop("username", f"user{i}"),
        password=kwargs.pop("password", PASSWORD),
        first_name=kwargs.pop("first_name", "Test"),
        last_name=kwargs.pop("last_name", f"User{i}"),
        role=role,
        **kwargs,
    )


def make_office(**kwargs):
    i = _n()
    defaults = {
        "name": f"Test Clinic {i}",
        "slug": f"test-clinic-{i}",
        "address_line": "100 Test Way",
        "city": "Salt Lake City",
        "postal_code": "84101",
        "phone": "(801) 555-0100",
    }
    defaults.update(kwargs)
    return Office.objects.create(**defaults)


def make_specialty(**kwargs):
    i = _n()
    defaults = {"name": f"Specialty {i}", "slug": f"specialty-{i}"}
    defaults.update(kwargs)
    return Specialty.objects.create(**defaults)


def make_plan(**kwargs):
    i = _n()
    defaults = {"code": f"plan-{i}", "name": f"Plan {i}", "carrier": "Test Carrier", "plan_type": "PPO"}
    defaults.update(kwargs)
    return InsurancePlan.objects.create(**defaults)


def make_appointment_type(code="follow-up", minutes=20, **kwargs):
    appointment_type, _ = AppointmentType.objects.get_or_create(
        code=code, defaults={"name": kwargs.pop("name", code.replace("-", " ").title()), "duration_minutes": minutes, **kwargs}
    )
    return appointment_type


def make_provider(*, office=None, specialty=None, with_user=True, weekdays=range(7), start=(8, 0), end=(17, 0),
                  plans=(), **kwargs):
    i = _n()
    office = office or make_office()
    specialty = specialty or make_specialty()
    user = make_user("doctor") if with_user else None
    defaults = {
        "first_name": "Pat",
        "last_name": f"Provider{i}",
        "credentials": "MD",
        "slug": f"provider-{i}",
        "title": "Family Medicine Physician",
        "gender": "F",
    }
    defaults.update(kwargs)
    provider = Provider.objects.create(user=user, specialty=specialty, **defaults)
    provider.offices.add(office)
    if plans:
        provider.insurance_plans.set(plans)
    for weekday in weekdays:
        ProviderSchedule.objects.create(
            provider=provider,
            office=office,
            weekday=weekday,
            start_time=datetime.time(*start),
            end_time=datetime.time(*end),
        )
    return provider


def make_patient(*, provider=None, with_user=True, **kwargs):
    i = _n()
    user = make_user("patient") if with_user else None
    defaults = {
        "mrn": f"T{i:07d}",
        "first_name": "Jamie",
        "last_name": f"Patient{i}",
        "date_of_birth": datetime.date(1985, 6, 15),
        "sex": "F",
        "phone": "(385) 555-0101",
        "email": f"patient{i}@example.com",
    }
    defaults.update(kwargs)
    return Patient.objects.create(user=user, primary_provider=provider, **defaults)


def make_appointment(*, patient, provider, start, office=None, appointment_type=None, status=Appointment.Status.SCHEDULED, **kwargs):
    appointment_type = appointment_type or make_appointment_type()
    office = office or provider.offices.first()
    return Appointment.objects.create(
        patient=patient,
        provider=provider,
        office=office,
        appointment_type=appointment_type,
        start=start,
        end=start + datetime.timedelta(minutes=appointment_type.duration_minutes),
        status=status,
        **kwargs,
    )


def make_visit(*, patient, provider, status=Visit.Status.SIGNED, **kwargs):
    defaults = {
        "visit_date": timezone.now() - datetime.timedelta(days=30),
        "visit_type": "Follow-up visit",
        "chief_complaint": "Follow-up",
        "assessment": "1. Doing well.",
        "plan": "- Continue current plan.",
        "patient_instructions": "Keep up the good work.",
        "status": status,
    }
    defaults.update(kwargs)
    if status == Visit.Status.SIGNED and "signed_at" not in defaults:
        defaults["signed_at"] = defaults["visit_date"]
    return Visit.objects.create(patient=patient, provider=provider, office=provider.offices.first(), **defaults)


def make_thread(*, patient, category=MessageThread.Category.APPOINTMENTS, body="Hello", **kwargs):
    thread = MessageThread(patient=patient, category=category, subject=kwargs.pop("subject", "Question"), **kwargs)
    thread.route()
    thread.save()
    Message.objects.create(thread=thread, sender=patient.user, sender_name=patient.full_name, from_patient=True, body=body)
    return thread
