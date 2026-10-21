import datetime

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import User
from audit.models import AuditLog
from audit.utils import log_event
from clinic.models import Appointment, LabResult, MessageThread, Patient, Provider, Visit
from clinic.services import patients_for_provider, provider_can_view_patient, reply_to_thread

from .forms import ReplyForm, VisitNoteForm

doctor_required = role_required(User.Role.DOCTOR)


def current_provider(request):
    try:
        return request.user.provider
    except Provider.DoesNotExist as exc:
        raise Http404("No provider profile is linked to this account.") from exc


def _require_chart_access(request, provider, patient):
    if not provider_can_view_patient(provider, patient):
        log_event(request, AuditLog.Action.ACCESS_DENIED, patient=patient, reason="no care relationship")
        raise PermissionDenied


def _day_bounds(day):
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.datetime.combine(day, datetime.time.min), tz)
    return start, start + datetime.timedelta(days=1)


@doctor_required
def dashboard(request):
    provider = current_provider(request)
    today = timezone.localdate()
    start, end = _day_bounds(today)
    todays = (
        provider.appointments.filter(start__gte=start, start__lt=end)
        .exclude(status=Appointment.Status.CANCELLED)
        .select_related("patient", "office", "appointment_type")
        .order_by("start")
    )
    drafts = provider.visits.filter(status=Visit.Status.DRAFT).select_related("patient").order_by("visit_date")
    inbox = MessageThread.objects.filter(
        queue=MessageThread.Queue.CLINICAL, assigned_provider=provider, status=MessageThread.Status.OPEN
    ).select_related("patient")
    my_patients = patients_for_provider(provider)
    abnormal_labs = (
        LabResult.objects.filter(
            patient__in=my_patients,
            ordered_by=provider,
            collected_on__gte=today - datetime.timedelta(days=60),
        )
        .exclude(flag=LabResult.Flag.NORMAL)
        .select_related("patient")[:8]
    )
    context = {
        "provider": provider,
        "today": today,
        "todays": todays,
        "drafts": drafts,
        "inbox": inbox[:6],
        "inbox_count": inbox.count(),
        "awaiting_count": sum(1 for t in inbox if t.awaiting_practice_reply),
        "abnormal_labs": abnormal_labs,
        "panel_size": my_patients.count(),
        "now": timezone.now(),
    }
    return render(request, "clinician/dashboard.html", context)


@doctor_required
def schedule(request):
    provider = current_provider(request)
    try:
        day = datetime.date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        day = timezone.localdate()
    start, end = _day_bounds(day)
    appointments = (
        provider.appointments.filter(start__gte=start, start__lt=end)
        .select_related("patient", "office", "appointment_type")
        .order_by("start")
    )
    blocks = provider.schedule_blocks.filter(weekday=day.weekday()).select_related("office")
    context = {
        "provider": provider,
        "day": day,
        "prev_day": day - datetime.timedelta(days=1),
        "next_day": day + datetime.timedelta(days=1),
        "appointments": appointments,
        "blocks": blocks,
    }
    return render(request, "clinician/schedule.html", context)


@doctor_required
def patient_list(request):
    provider = current_provider(request)
    patients = patients_for_provider(provider).select_related("primary_provider", "insurance_plan")
    query = request.GET.get("q", "").strip()
    if query:
        patients = patients.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(mrn__icontains=query)
        )
    return render(
        request, "clinician/patient_list.html", {"provider": provider, "patients": patients, "query": query}
    )


@doctor_required
def chart(request, pk):
    provider = current_provider(request)
    patient = get_object_or_404(
        Patient.objects.select_related("primary_provider", "primary_office", "insurance_plan"), pk=pk
    )
    _require_chart_access(request, provider, patient)
    log_event(request, AuditLog.Action.VIEW_CHART, patient=patient, target=patient)
    now = timezone.now()
    labs = patient.lab_results.select_related("ordered_by")[:30]
    context = {
        "provider": provider,
        "patient": patient,
        "allergies": patient.allergies.all(),
        "problems": patient.problems.all(),
        "medications": patient.medications.select_related("prescriber"),
        "visits": patient.visits.select_related("provider", "office")[:20],
        "labs": labs,
        "upcoming": patient.appointments.filter(start__gt=now)
        .exclude(status=Appointment.Status.CANCELLED)
        .select_related("provider", "office")
        .order_by("start"),
        "threads": patient.message_threads.filter(queue=MessageThread.Queue.CLINICAL)[:5],
        "latest_vitals": patient.visits.exclude(blood_pressure="").first(),
    }
    return render(request, "clinician/chart.html", context)


@doctor_required
def visit_detail(request, pk):
    provider = current_provider(request)
    visit = get_object_or_404(Visit.objects.select_related("patient", "provider", "office", "signed_by"), pk=pk)
    _require_chart_access(request, provider, visit.patient)
    log_event(request, AuditLog.Action.VIEW_VISIT, patient=visit.patient, target=visit)
    can_edit = visit.provider_id == provider.pk and not visit.is_signed
    return render(
        request, "clinician/visit_detail.html", {"provider": provider, "visit": visit, "can_edit": can_edit}
    )


@doctor_required
def start_note(request, appointment_pk):
    provider = current_provider(request)
    appointment = get_object_or_404(Appointment, pk=appointment_pk, provider=provider)
    if appointment.status in (Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW):
        messages.error(request, "Notes can't be started for cancelled or no-show appointments.")
        return redirect("clinician:schedule")
    visit, created = Visit.objects.get_or_create(
        appointment=appointment,
        defaults={
            "patient": appointment.patient,
            "provider": provider,
            "office": appointment.office,
            "visit_date": appointment.start,
            "visit_type": appointment.appointment_type.name,
            "chief_complaint": appointment.reason,
        },
    )
    if created:
        log_event(request, AuditLog.Action.SAVE_VISIT_NOTE, patient=visit.patient, target=visit, created=True)
    return redirect("clinician:edit_note", pk=visit.pk)


@doctor_required
def edit_note(request, pk):
    provider = current_provider(request)
    visit = get_object_or_404(Visit.objects.select_related("patient", "appointment"), pk=pk)
    if visit.provider_id != provider.pk:
        log_event(request, AuditLog.Action.ACCESS_DENIED, patient=visit.patient, reason="not author of note")
        raise PermissionDenied
    if visit.is_signed:
        messages.info(request, "This note is signed and can no longer be edited.")
        return redirect("clinician:visit_detail", pk=visit.pk)

    _require_chart_access(request, provider, visit.patient)
    form = VisitNoteForm(request.POST or None, instance=visit)
    if request.method == "POST" and form.is_valid():
        signing = "sign" in request.POST
        if signing and (not form.cleaned_data.get("assessment") or not form.cleaned_data.get("plan")):
            form.add_error(None, "Assessment and plan are required before signing.")
        else:
            visit = form.save()
            log_event(request, AuditLog.Action.SAVE_VISIT_NOTE, patient=visit.patient, target=visit)
            if signing:
                visit.sign(request.user)
                if visit.appointment and visit.appointment.status != Appointment.Status.COMPLETED:
                    visit.appointment.status = Appointment.Status.COMPLETED
                    visit.appointment.save(update_fields=["status", "updated_at"])
                log_event(request, AuditLog.Action.SIGN_VISIT_NOTE, patient=visit.patient, target=visit)
                messages.success(request, "Note signed. The after-visit summary is now visible to the patient.")
                return redirect("clinician:visit_detail", pk=visit.pk)
            messages.success(request, "Draft saved.")
            return redirect("clinician:edit_note", pk=visit.pk)
    context = {
        "provider": provider,
        "visit": visit,
        "patient": visit.patient,
        "form": form,
        "allergies": visit.patient.allergies.all(),
        "problems": visit.patient.problems.filter(status="active"),
        "medications": visit.patient.medications.filter(is_active=True),
    }
    return render(request, "clinician/note_form.html", context)


@doctor_required
def inbox(request):
    provider = current_provider(request)
    status = request.GET.get("status", "open")
    threads = MessageThread.objects.filter(
        queue=MessageThread.Queue.CLINICAL, assigned_provider=provider
    ).select_related("patient")
    if status in MessageThread.Status.values:
        threads = threads.filter(status=status)
    return render(
        request,
        "clinician/inbox.html",
        {"provider": provider, "threads": threads.prefetch_related("messages"), "status": status},
    )


@doctor_required
def thread_detail(request, pk):
    provider = current_provider(request)
    thread = get_object_or_404(
        MessageThread.objects.select_related("patient"),
        pk=pk,
        queue=MessageThread.Queue.CLINICAL,
        assigned_provider=provider,
    )
    form = ReplyForm(request.POST or None)
    if request.method == "POST":
        if request.POST.get("action") == "close":
            thread.status = MessageThread.Status.CLOSED
            thread.staff_has_unread = False
            thread.save(update_fields=["status", "staff_has_unread"])
            log_event(request, AuditLog.Action.CLOSE_THREAD, patient=thread.patient, target=thread)
            messages.success(request, "Conversation closed.")
            return redirect("clinician:inbox")
        if form.is_valid():
            reply_to_thread(
                thread=thread,
                body=form.cleaned_data["body"],
                sender=request.user,
                from_patient=False,
                sender_name=provider.display_name,
            )
            log_event(request, AuditLog.Action.SEND_MESSAGE, patient=thread.patient, target=thread, by="clinician")
            messages.success(request, "Reply sent to patient.")
            return redirect("clinician:thread", pk=thread.pk)
    elif thread.staff_has_unread:
        thread.staff_has_unread = False
        thread.save(update_fields=["staff_has_unread"])
    context = {
        "provider": provider,
        "thread": thread,
        "thread_messages": thread.messages.all(),
        "form": form,
        "patient": thread.patient,
        "medications": thread.patient.medications.filter(is_active=True),
        "problems": thread.patient.problems.filter(status="active"),
        "recent_labs": thread.patient.lab_results.all()[:6],
    }
    return render(request, "clinician/thread.html", context)
