from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from audit.models import AuditLog
from audit.utils import log_event
from clinic.models import InsurancePlan, Office, PolicyDocument, Provider, Specialty
from clinic.services import available_slots, next_available_slot

from .forms import AppointmentRequestForm


def home(request):
    specialties = Specialty.objects.annotate(provider_count=Count("providers")).order_by("name")
    offices = Office.objects.prefetch_related("hours")
    context = {
        "specialties": specialties,
        "offices": offices,
        "resources": PolicyDocument.objects.filter(is_public=True)[:4],
        "provider_count": Provider.objects.filter(is_active=True).count(),
        "accepting_count": Provider.objects.filter(is_active=True, accepting_new_patients=True).count(),
    }
    return render(request, "public/home.html", context)


def _all_languages():
    languages = set()
    for value in Provider.objects.filter(is_active=True).values_list("languages", flat=True):
        languages.update(lang.strip() for lang in value.split(",") if lang.strip())
    return sorted(languages)


def provider_list(request):
    params = request.GET
    providers = Provider.objects.filter(is_active=True).select_related("specialty").prefetch_related("offices")
    query = params.get("q", "").strip()
    if query:
        providers = providers.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(specialty__name__icontains=query)
        )
    if params.get("specialty"):
        providers = providers.filter(specialty__slug=params["specialty"])
    if params.get("office"):
        providers = providers.filter(offices__slug=params["office"])
    if params.get("insurance"):
        providers = providers.filter(insurance_plans__code=params["insurance"])
    if params.get("language"):
        providers = providers.filter(languages__icontains=params["language"])
    if params.get("gender"):
        providers = providers.filter(gender=params["gender"])
    if params.get("accepting"):
        providers = providers.filter(accepting_new_patients=True)
    if params.get("telehealth"):
        providers = providers.filter(offers_telehealth=True)
    providers = providers.distinct().order_by("last_name", "first_name")

    page = Paginator(providers, 10).get_page(params.get("page"))
    now = timezone.now()
    results = [(provider, next_available_slot(provider, now=now)) for provider in page]
    context = {
        "page": page,
        "results": results,
        "total": providers.count(),
        "filters": params,
        "specialties": Specialty.objects.all(),
        "offices": Office.objects.all(),
        "plans": InsurancePlan.objects.filter(is_active=True),
        "languages": _all_languages(),
        "gender_choices": Provider.Gender.choices,
    }
    return render(request, "public/provider_list.html", context)


def provider_detail(request, slug):
    provider = get_object_or_404(
        Provider.objects.select_related("specialty").prefetch_related("offices", "insurance_plans"),
        slug=slug,
        is_active=True,
    )
    now = timezone.now()
    slots = available_slots(provider, timezone.localdate(), days=21, now=now, limit=8)
    schedule = provider.schedule_blocks.select_related("office").order_by("weekday", "start_time")
    days = {}
    for block in schedule:
        days.setdefault(block.get_weekday_display(), set()).add(block.office.name)
    context = {
        "provider": provider,
        "slots": slots,
        "schedule_days": [(day, sorted(offices)) for day, offices in days.items()],
    }
    return render(request, "public/provider_detail.html", context)


def location_list(request):
    offices = Office.objects.prefetch_related("hours").annotate(provider_count=Count("providers"))
    return render(request, "public/location_list.html", {"offices": offices})


def location_detail(request, slug):
    office = get_object_or_404(Office.objects.prefetch_related("hours"), slug=slug)
    providers = office.providers.filter(is_active=True).select_related("specialty")
    return render(request, "public/location_detail.html", {"office": office, "providers": providers})


def insurance_list(request):
    plans = InsurancePlan.objects.filter(is_active=True).annotate(provider_count=Count("providers"))
    specialties = Specialty.objects.all()
    matrix = []
    for plan in plans:
        accepted = set(
            plan.providers.filter(is_active=True).values_list("specialty__name", flat=True).distinct()
        )
        matrix.append((plan, [(s, s.name in accepted) for s in specialties]))
    return render(request, "public/insurance.html", {"matrix": matrix, "specialties": specialties})


def resource_list(request):
    documents = PolicyDocument.objects.filter(is_public=True)
    groups = {}
    for doc in documents:
        groups.setdefault(doc.get_category_display(), []).append(doc)
    return render(request, "public/resource_list.html", {"groups": groups.items()})


def resource_detail(request, slug):
    document = get_object_or_404(PolicyDocument, slug=slug, is_public=True)
    others = PolicyDocument.objects.filter(is_public=True).exclude(pk=document.pk)
    return render(request, "public/resource_detail.html", {"document": document, "others": others})


def request_appointment(request):
    if request.user.is_authenticated and getattr(request.user, "is_patient", False):
        return redirect("portal:request_appointment")
    initial = {}
    for field, model, lookup in (
        ("preferred_provider", Provider, "slug"),
        ("preferred_specialty", Specialty, "slug"),
        ("preferred_office", Office, "slug"),
    ):
        key = field.replace("preferred_", "")
        if request.GET.get(key):
            initial[field] = model.objects.filter(**{lookup: request.GET[key]}).first()
    if initial.get("preferred_provider") and not initial.get("preferred_specialty"):
        initial["preferred_specialty"] = initial["preferred_provider"].specialty

    form = AppointmentRequestForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        appointment_request = form.save()
        log_event(request, AuditLog.Action.CREATE_APPOINTMENT_REQUEST, target=appointment_request, source="website")
        request.session["last_request_reference"] = appointment_request.reference
        return redirect("public:request_thanks")
    return render(request, "public/request_appointment.html", {"form": form})


def request_thanks(request):
    reference = request.session.get("last_request_reference")
    if not reference:
        return redirect("public:request_appointment")
    return render(request, "public/request_thanks.html", {"reference": reference})


def permission_denied(request, exception=None):
    return render(request, "403.html", status=403)


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)
