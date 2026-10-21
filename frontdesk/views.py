import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import dateformat, timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User
from audit.models import AuditLog
from audit.utils import log_event
from clinic.models import (
    Appointment,
    AppointmentRequest,
    AppointmentType,
    MessageThread,
    Office,
    Patient,
    Provider,
)
from clinic.services import SlotUnavailable, book_appointment, parse_slot_value, reply_to_thread

from .forms import CancelForm, DeclineForm, NewPatientDetailsForm, ReplyForm, StaffNotesForm
from .scheduling import slot_picker_context

front_office_required = role_required(User.Role.FRONT_OFFICE)


def _day_bounds(day):
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.datetime.combine(day, datetime.time.min), tz)
    return start, start + datetime.timedelta(days=1)


@front_office_required
def dashboard(request):
    today = timezone.localdate()
    start, end = _day_bounds(today)
    office = request.user.office
    todays = Appointment.objects.filter(start__gte=start, start__lt=end).exclude(status=Appointment.Status.CANCELLED)
    if office is not None:
        todays = todays.filter(office=office)
    threads = MessageThread.objects.filter(queue=MessageThread.Queue.FRONT_OFFICE, status=MessageThread.Status.OPEN)
    context = {
        "office": office,
        "today": today,
        "counts": {
            "new_requests": AppointmentRequest.objects.filter(status=AppointmentRequest.Status.SUBMITTED).count(),
            "under_review": AppointmentRequest.objects.filter(status=AppointmentRequest.Status.UNDER_REVIEW).count(),
            "unread_messages": threads.filter(staff_has_unread=True).count(),
            "todays_appointments": todays.count(),
            "checked_in": todays.filter(status=Appointment.Status.CHECKED_IN).count(),
        },
        "todays": todays.select_related("patient", "provider", "appointment_type", "office")[:12],
        "recent_requests": AppointmentRequest.objects.filter(status__in=AppointmentRequest.OPEN_STATUSES)
        .select_related("preferred_specialty", "preferred_office")[:6],
        "recent_threads": threads.select_related("patient")[:6],
    }
    return render(request, "frontdesk/dashboard.html", context)


@front_office_required
def request_list(request):
    status = request.GET.get("status", "open")
    requests_qs = AppointmentRequest.objects.select_related(
        "preferred_specialty", "preferred_provider", "preferred_office", "patient", "insurance_plan"
    )
    if status == "open":
        requests_qs = requests_qs.filter(status__in=AppointmentRequest.OPEN_STATUSES)
    elif status in AppointmentRequest.Status.values:
        requests_qs = requests_qs.filter(status=status)
    source = request.GET.get("source")
    if source in AppointmentRequest.Source.values:
        requests_qs = requests_qs.filter(source=source)
    query = request.GET.get("q", "").strip()
    if query:
        requests_qs = requests_qs.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(reference__icontains=query)
        )
    page = Paginator(requests_qs, 15).get_page(request.GET.get("page"))
    context = {
        "page": page,
        "status": status,
        "source": source,
        "query": query,
        "status_choices": AppointmentRequest.Status.choices,
        "source_choices": AppointmentRequest.Source.choices,
    }
    return render(request, "frontdesk/request_list.html", context)


@front_office_required
def request_detail(request, pk):
    appointment_request = get_object_or_404(
        AppointmentRequest.objects.select_related(
            "patient", "preferred_specialty", "preferred_provider", "preferred_office", "insurance_plan", "appointment"
        ),
        pk=pk,
    )
    matches = []
    if appointment_request.patient is None:
        matches = Patient.objects.filter(
            last_name__iexact=appointment_request.last_name, date_of_birth=appointment_request.date_of_birth
        )
    context = {
        "req": appointment_request,
        "matches": matches,
        "notes_form": StaffNotesForm(initial={"staff_notes": appointment_request.staff_notes}),
        "decline_form": DeclineForm(),
        "new_patient_form": NewPatientDetailsForm(),
    }
    if appointment_request.is_open:
        context.update(
            slot_picker_context(
                request.GET,
                default_provider=appointment_request.preferred_provider,
                patient_plan=appointment_request.insurance_plan,
            )
        )
    return render(request, "frontdesk/request_detail.html", context)


@front_office_required
@require_POST
def request_action(request, pk):
    appointment_request = get_object_or_404(AppointmentRequest, pk=pk)
    action = request.POST.get("action")
    if not appointment_request.is_open and action != "save_notes":
        messages.error(request, "This request is already closed.")
        return redirect("frontdesk:request_detail", pk=pk)

    if action == "start_review":
        appointment_request.status = AppointmentRequest.Status.UNDER_REVIEW
        appointment_request.handled_by = request.user
        appointment_request.save(update_fields=["status", "handled_by", "updated_at"])
        messages.success(request, "Request marked as under review.")
    elif action == "save_notes":
        form = StaffNotesForm(request.POST)
        if form.is_valid():
            appointment_request.staff_notes = form.cleaned_data["staff_notes"]
            appointment_request.save(update_fields=["staff_notes", "updated_at"])
            messages.success(request, "Notes saved.")
    elif action == "decline":
        form = DeclineForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please enter a reason for declining.")
            return redirect("frontdesk:request_detail", pk=pk)
        appointment_request.status = AppointmentRequest.Status.DECLINED
        appointment_request.decline_reason = form.cleaned_data["decline_reason"]
        appointment_request.handled_by = request.user
        appointment_request.save(update_fields=["status", "decline_reason", "handled_by", "updated_at"])
        log_event(
            request,
            AuditLog.Action.DECLINE_APPOINTMENT_REQUEST,
            patient=appointment_request.patient,
            target=appointment_request,
        )
        messages.success(request, "Request declined.")
    elif action == "link_patient":
        patient = get_object_or_404(Patient, pk=request.POST.get("patient_id"))
        appointment_request.patient = patient
        appointment_request.save(update_fields=["patient", "updated_at"])
        messages.success(request, f"Linked to existing patient {patient.full_name} ({patient.mrn}).")
    elif action == "book":
        return _book_request(request, appointment_request)
    else:
        messages.error(request, "Unknown action.")
        return redirect("frontdesk:request_detail", pk=pk)
    log_event(request, AuditLog.Action.UPDATE_APPOINTMENT_REQUEST, target=appointment_request, step=action)
    return redirect("frontdesk:request_detail", pk=pk)


def _resolve_booking(request):
    provider = get_object_or_404(Provider, pk=request.POST.get("provider"))
    appointment_type = get_object_or_404(AppointmentType, pk=request.POST.get("appointment_type"))
    try:
        office_id, start = parse_slot_value(request.POST.get("slot", ""))
    except ValueError:
        return None
    office = get_object_or_404(Office, pk=office_id)
    return provider, appointment_type, office, start


def _book_request(request, appointment_request):
    resolved = _resolve_booking(request)
    if resolved is None:
        messages.error(request, "Please choose an available time.")
        return redirect("frontdesk:request_detail", pk=appointment_request.pk)
    provider, appointment_type, office, start = resolved

    patient = appointment_request.patient
    if patient is None:
        details = NewPatientDetailsForm(request.POST)
        sex = details.cleaned_data["sex"] if details.is_valid() else Patient.Sex.OTHER
        patient = Patient.objects.create(
            mrn=Patient.generate_mrn(),
            first_name=appointment_request.first_name,
            last_name=appointment_request.last_name,
            date_of_birth=appointment_request.date_of_birth,
            sex=sex,
            email=appointment_request.email,
            phone=appointment_request.phone,
            insurance_plan=appointment_request.insurance_plan,
            primary_provider=provider,
            primary_office=office if not office.is_virtual else provider.offices.filter(is_virtual=False).first(),
        )
        log_event(request, AuditLog.Action.REGISTER_PATIENT, patient=patient, target=patient)

    try:
        appointment = book_appointment(
            patient=patient,
            provider=provider,
            office=office,
            appointment_type=appointment_type,
            start=start,
            created_by=request.user,
            reason=appointment_request.reason,
        )
    except SlotUnavailable as exc:
        messages.error(request, str(exc))
        return redirect("frontdesk:request_detail", pk=appointment_request.pk)

    appointment_request.patient = patient
    appointment_request.appointment = appointment
    appointment_request.status = AppointmentRequest.Status.SCHEDULED
    appointment_request.handled_by = request.user
    appointment_request.save(update_fields=["patient", "appointment", "status", "handled_by", "updated_at"])
    log_event(request, AuditLog.Action.SCHEDULE_APPOINTMENT, patient=patient, target=appointment, request_reference=appointment_request.reference)
    when = dateformat.format(timezone.localtime(appointment.start), r"D M j \a\t g:i A")
    messages.success(request, f"Scheduled {patient.full_name} with {provider.short_name} on {when}.")
    return redirect("frontdesk:request_detail", pk=appointment_request.pk)


@front_office_required
def schedule(request):
    try:
        day = datetime.date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        day = timezone.localdate()
    office_slug = request.GET.get("office")
    if office_slug is None and request.user.office is not None:
        office_slug = request.user.office.slug
    start, end = _day_bounds(day)
    appointments_qs = Appointment.objects.filter(start__gte=start, start__lt=end).select_related(
        "patient", "provider", "office", "appointment_type"
    )
    selected_office = Office.objects.filter(slug=office_slug).first() if office_slug else None
    if selected_office is not None:
        appointments_qs = appointments_qs.filter(office=selected_office)
    context = {
        "day": day,
        "prev_day": day - datetime.timedelta(days=1),
        "next_day": day + datetime.timedelta(days=1),
        "offices": Office.objects.all(),
        "selected_office": selected_office,
        "appointments": appointments_qs.order_by("start", "provider__last_name"),
        "cancel_form": CancelForm(),
        "now": timezone.now(),
    }
    return render(request, "frontdesk/schedule.html", context)


@front_office_required
@require_POST
def appointment_action(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    action = request.POST.get("action")
    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = "frontdesk:schedule"
    if action == "check_in" and appointment.status == Appointment.Status.SCHEDULED:
        appointment.status = Appointment.Status.CHECKED_IN
        appointment.checked_in_at = timezone.now()
        audit_action = AuditLog.Action.CHECK_IN
    elif action == "no_show" and appointment.status == Appointment.Status.SCHEDULED:
        appointment.status = Appointment.Status.NO_SHOW
        audit_action = AuditLog.Action.MARK_NO_SHOW
    elif action == "cancel" and appointment.status in (Appointment.Status.SCHEDULED, Appointment.Status.CHECKED_IN):
        form = CancelForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please enter a cancellation reason.")
            return redirect(next_url)
        appointment.status = Appointment.Status.CANCELLED
        appointment.cancellation_reason = form.cleaned_data["reason"]
        audit_action = AuditLog.Action.CANCEL_APPOINTMENT
    else:
        messages.error(request, "That action isn't available for this appointment.")
        return redirect(next_url)
    appointment.save()
    log_event(request, audit_action, patient=appointment.patient, target=appointment)
    messages.success(request, f"{appointment.patient.full_name}: {appointment.get_status_display().lower()}.")
    return redirect(next_url)


@front_office_required
def message_list(request):
    status = request.GET.get("status", "open")
    threads = MessageThread.objects.filter(queue=MessageThread.Queue.FRONT_OFFICE).select_related("patient")
    if status in MessageThread.Status.values:
        threads = threads.filter(status=status)
    category = request.GET.get("category")
    if category in MessageThread.FRONT_OFFICE_CATEGORIES:
        threads = threads.filter(category=category)
    page = Paginator(threads.prefetch_related("messages"), 20).get_page(request.GET.get("page"))
    categories = [c for c in MessageThread.Category.choices if c[0] in MessageThread.FRONT_OFFICE_CATEGORIES]
    return render(
        request,
        "frontdesk/message_list.html",
        {"page": page, "status": status, "category": category, "categories": categories},
    )


@front_office_required
def thread_detail(request, pk):
    thread = get_object_or_404(
        MessageThread.objects.select_related("patient"), pk=pk, queue=MessageThread.Queue.FRONT_OFFICE
    )
    form = ReplyForm(request.POST or None)
    if request.method == "POST":
        if request.POST.get("action") == "close":
            thread.status = MessageThread.Status.CLOSED
            thread.staff_has_unread = False
            thread.save(update_fields=["status", "staff_has_unread"])
            log_event(request, AuditLog.Action.CLOSE_THREAD, patient=thread.patient, target=thread)
            messages.success(request, "Conversation closed.")
            return redirect("frontdesk:messages")
        if form.is_valid():
            reply_to_thread(
                thread=thread,
                body=form.cleaned_data["body"],
                sender=request.user,
                from_patient=False,
                sender_name=f"{request.user.display_name}, Front Office",
            )
            log_event(request, AuditLog.Action.SEND_MESSAGE, patient=thread.patient, target=thread, by="front_office")
            messages.success(request, "Reply sent to patient.")
            return redirect("frontdesk:thread", pk=thread.pk)
    elif thread.staff_has_unread:
        thread.staff_has_unread = False
        thread.save(update_fields=["staff_has_unread"])
    return render(
        request,
        "frontdesk/thread.html",
        {"thread": thread, "thread_messages": thread.messages.all(), "form": form},
    )


@front_office_required
def patient_search(request):
    query = request.GET.get("q", "").strip()
    patients = Patient.objects.none()
    if query:
        filters = Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(mrn__icontains=query) | Q(
            phone__icontains=query
        )
        try:
            filters |= Q(date_of_birth=datetime.date.fromisoformat(query))
        except ValueError:
            pass
        parts = query.split()
        if len(parts) == 2:
            filters |= Q(first_name__icontains=parts[0], last_name__icontains=parts[1])
        patients = Patient.objects.filter(filters).select_related("primary_provider", "insurance_plan")[:50]
    return render(request, "frontdesk/patient_search.html", {"query": query, "patients": patients})


@front_office_required
def patient_detail(request, pk):
    patient = get_object_or_404(
        Patient.objects.select_related("primary_provider", "primary_office", "insurance_plan"), pk=pk
    )
    log_event(request, AuditLog.Action.VIEW_PATIENT_PROFILE, patient=patient, target=patient)
    now = timezone.now()
    appointments_qs = patient.appointments.select_related("provider", "office", "appointment_type")
    context = {
        "patient": patient,
        "upcoming": appointments_qs.filter(start__gt=now).order_by("start"),
        "past": appointments_qs.filter(start__lte=now).order_by("-start")[:10],
        "requests": patient.appointment_requests.all()[:10],
        "threads": patient.message_threads.filter(queue=MessageThread.Queue.FRONT_OFFICE)[:10],
        "cancel_form": CancelForm(),
        "now": now,
    }
    return render(request, "frontdesk/patient_detail.html", context)


@front_office_required
def book_for_patient(request, pk):
    patient = get_object_or_404(Patient.objects.select_related("primary_provider", "insurance_plan"), pk=pk)
    if request.method == "POST":
        resolved = _resolve_booking(request)
        if resolved is None:
            messages.error(request, "Please choose an available time.")
            return redirect("frontdesk:book_for_patient", pk=pk)
        provider, appointment_type, office, start = resolved
        try:
            appointment = book_appointment(
                patient=patient,
                provider=provider,
                office=office,
                appointment_type=appointment_type,
                start=start,
                created_by=request.user,
                reason=request.POST.get("reason", ""),
            )
        except SlotUnavailable as exc:
            messages.error(request, str(exc))
            return redirect("frontdesk:book_for_patient", pk=pk)
        log_event(request, AuditLog.Action.SCHEDULE_APPOINTMENT, patient=patient, target=appointment, source="phone")
        messages.success(request, "Appointment booked.")
        return redirect("frontdesk:patient_detail", pk=pk)
    context = {"patient": patient}
    context.update(
        slot_picker_context(request.GET, default_provider=patient.primary_provider, patient_plan=patient.insurance_plan)
    )
    return render(request, "frontdesk/book_for_patient.html", context)
