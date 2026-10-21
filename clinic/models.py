"""Core data model for Alderwick Family Health.

All data in this application is synthetic. Do not enter real patient information.
"""

import datetime
import secrets

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

WEEKDAY_CHOICES = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]

PHYSICIAN_CREDENTIALS = {"MD", "DO"}


# ---------------------------------------------------------------------------
# Practice directory
# ---------------------------------------------------------------------------


class Office(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    address_line = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=2, default="UT")
    postal_code = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    is_virtual = models.BooleanField(default=False, help_text="Telehealth-only location.")
    description = models.TextField(blank=True)
    services = models.TextField(blank=True, help_text="One service per line.")
    parking_notes = models.TextField(blank=True)
    accessibility_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["is_virtual", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("public:location_detail", args=[self.slug])

    @property
    def full_address(self):
        if self.is_virtual:
            return "Video visits from anywhere in Utah"
        return f"{self.address_line}, {self.city}, {self.state} {self.postal_code}"

    @property
    def service_list(self):
        return [line.strip() for line in self.services.splitlines() if line.strip()]

    def is_open_on(self, weekday):
        return self.hours.filter(weekday=weekday).exists()


class OfficeHours(models.Model):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name="hours")
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    opens = models.TimeField()
    closes = models.TimeField()

    class Meta:
        ordering = ["office", "weekday"]
        constraints = [models.UniqueConstraint(fields=["office", "weekday"], name="unique_office_weekday")]
        verbose_name_plural = "office hours"

    def __str__(self):
        return f"{self.office} {self.get_weekday_display()} {self.opens:%H:%M}-{self.closes:%H:%M}"


class Specialty(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "specialties"

    def __str__(self):
        return self.name


class InsurancePlan(models.Model):
    class PlanType(models.TextChoices):
        PPO = "PPO", "PPO"
        HMO = "HMO", "HMO"
        EPO = "EPO", "EPO"
        MEDICARE_ADVANTAGE = "MA", "Medicare Advantage"
        MEDICAID = "MCD", "Medicaid managed care"
        SELF_PAY = "SELF", "Self-pay"

    code = models.SlugField(unique=True)
    name = models.CharField(max_length=120, unique=True)
    carrier = models.CharField(max_length=120)
    plan_type = models.CharField(max_length=4, choices=PlanType.choices)
    member_services_phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Provider(models.Model):
    class Gender(models.TextChoices):
        FEMALE = "F", "Female"
        MALE = "M", "Male"
        NONBINARY = "X", "Nonbinary"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="provider"
    )
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    credentials = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name="providers")
    gender = models.CharField(max_length=1, choices=Gender.choices)
    languages = models.CharField(max_length=200, default="English", help_text="Comma-separated.")
    offices = models.ManyToManyField(Office, related_name="providers")
    insurance_plans = models.ManyToManyField(InsurancePlan, related_name="providers", blank=True)
    accepting_new_patients = models.BooleanField(default=True)
    offers_telehealth = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    education = models.TextField(blank=True, help_text="One entry per line.")
    board_certification = models.CharField(max_length=200, blank=True)
    practicing_since = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.display_name

    def get_absolute_url(self):
        return reverse("public:provider_detail", args=[self.slug])

    @property
    def is_physician(self):
        return self.credentials in PHYSICIAN_CREDENTIALS

    @property
    def display_name(self):
        prefix = "Dr. " if self.is_physician else ""
        return f"{prefix}{self.first_name} {self.last_name}, {self.credentials}"

    @property
    def short_name(self):
        if self.is_physician:
            return f"Dr. {self.last_name}"
        return f"{self.first_name} {self.last_name}, {self.credentials}"

    @property
    def initials(self):
        return f"{self.first_name[:1]}{self.last_name[:1]}"

    @property
    def language_list(self):
        return [lang.strip() for lang in self.languages.split(",") if lang.strip()]

    @property
    def education_list(self):
        return [line.strip() for line in self.education.splitlines() if line.strip()]

    def accepts(self, plan):
        return plan is not None and self.insurance_plans.filter(pk=plan.pk).exists()


class ProviderSchedule(models.Model):
    """A recurring weekly block when a provider sees patients at an office."""

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="schedule_blocks")
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name="schedule_blocks")
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["provider", "weekday", "start_time"]

    def __str__(self):
        return f"{self.provider.short_name} {self.get_weekday_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M} @ {self.office}"


class AppointmentType(models.Model):
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    duration_minutes = models.PositiveIntegerField(default=20)
    description = models.CharField(max_length=255, blank=True)
    is_telehealth = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.duration_minutes} min)"


# ---------------------------------------------------------------------------
# Patients and clinical record
# ---------------------------------------------------------------------------


class Patient(models.Model):
    class Sex(models.TextChoices):
        FEMALE = "F", "Female"
        MALE = "M", "Male"
        OTHER = "X", "Other / not listed"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="patient"
    )
    mrn = models.CharField("MRN", max_length=12, unique=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    preferred_name = models.CharField(max_length=60, blank=True)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=Sex.choices)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address_line = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=2, default="UT")
    postal_code = models.CharField(max_length=10, blank=True)
    preferred_language = models.CharField(max_length=40, default="English")
    insurance_plan = models.ForeignKey(
        InsurancePlan, null=True, blank=True, on_delete=models.SET_NULL, related_name="patients"
    )
    insurance_member_id = models.CharField(max_length=30, blank=True)
    primary_provider = models.ForeignKey(
        Provider, null=True, blank=True, on_delete=models.SET_NULL, related_name="primary_patients"
    )
    primary_office = models.ForeignKey(
        Office, null=True, blank=True, on_delete=models.SET_NULL, related_name="primary_patients"
    )
    guardian_name = models.CharField(max_length=120, blank=True, help_text="Parent or guardian for minors.")
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_relationship = models.CharField(max_length=40, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.mrn})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self):
        if self.preferred_name and self.preferred_name != self.first_name:
            return f"{self.first_name} “{self.preferred_name}” {self.last_name}"
        return self.full_name

    def age(self, on=None):
        on = on or timezone.localdate()
        dob = self.date_of_birth
        return on.year - dob.year - ((on.month, on.day) < (dob.month, dob.day))

    @property
    def age_today(self):
        return self.age()

    @property
    def is_minor(self):
        return self.age() < 18

    @staticmethod
    def generate_mrn():
        while True:
            candidate = f"AFH{secrets.randbelow(10**6):06d}"
            if not Patient.objects.filter(mrn=candidate).exists():
                return candidate


class Allergy(models.Model):
    class Severity(models.TextChoices):
        MILD = "mild", "Mild"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="allergies")
    substance = models.CharField(max_length=120)
    reaction = models.CharField(max_length=200, blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MILD)
    recorded_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["substance"]
        verbose_name_plural = "allergies"

    def __str__(self):
        return f"{self.substance} ({self.get_severity_display()})"


class Problem(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RESOLVED = "resolved", "Resolved"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="problems")
    description = models.CharField(max_length=200)
    icd10_code = models.CharField("ICD-10 code", max_length=10, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    onset_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["status", "description"]

    def __str__(self):
        return f"{self.description} [{self.icd10_code}]"


class Medication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medications")
    name = models.CharField(max_length=120)
    dose = models.CharField(max_length=60, blank=True)
    route = models.CharField(max_length=40, default="Oral")
    frequency = models.CharField(max_length=120, blank=True)
    instructions = models.CharField(max_length=255, blank=True)
    prescriber = models.ForeignKey(
        Provider, null=True, blank=True, on_delete=models.SET_NULL, related_name="prescriptions"
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_active", "name"]

    def __str__(self):
        return f"{self.name} {self.dose}".strip()


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CHECKED_IN = "checked_in", "Checked in"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No-show"

    # Statuses that occupy time on a provider's calendar.
    BLOCKING_STATUSES = (Status.SCHEDULED, Status.CHECKED_IN, Status.COMPLETED)

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT, related_name="appointments")
    office = models.ForeignKey(Office, on_delete=models.PROTECT, related_name="appointments")
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.PROTECT, related_name="appointments")
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    reason = models.CharField(max_length=255, blank=True)
    front_desk_notes = models.TextField(blank=True)
    cancellation_reason = models.CharField(max_length=255, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start"]

    def __str__(self):
        local = timezone.localtime(self.start)
        return f"{self.patient.full_name} with {self.provider.short_name} on {local:%Y-%m-%d %H:%M}"

    @property
    def duration_minutes(self):
        return int((self.end - self.start).total_seconds() // 60)

    def is_upcoming(self, now=None):
        now = now or timezone.now()
        return self.start > now and self.status == self.Status.SCHEDULED

    def patient_can_cancel(self, now=None):
        """Patients may cancel online up to 24 hours before the visit (see cancellation policy)."""
        now = now or timezone.now()
        return self.status == self.Status.SCHEDULED and self.start - now >= datetime.timedelta(hours=24)


class Visit(models.Model):
    """A clinical encounter and its note."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SIGNED = "signed", "Signed"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT, related_name="visits")
    office = models.ForeignKey(Office, null=True, blank=True, on_delete=models.SET_NULL, related_name="visits")
    appointment = models.OneToOneField(
        Appointment, null=True, blank=True, on_delete=models.SET_NULL, related_name="visit"
    )
    visit_date = models.DateTimeField()
    visit_type = models.CharField(max_length=80)
    chief_complaint = models.CharField(max_length=255, blank=True)
    blood_pressure = models.CharField(max_length=10, blank=True)
    heart_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    temperature_f = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    weight_lb = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    height_in = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    oxygen_saturation = models.PositiveSmallIntegerField(null=True, blank=True)
    subjective = models.TextField(blank=True)
    objective = models.TextField(blank=True)
    assessment = models.TextField(blank=True)
    plan = models.TextField(blank=True)
    patient_instructions = models.TextField(blank=True, help_text="After-visit summary shown in the patient portal.")
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.DRAFT)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-visit_date"]

    def __str__(self):
        return f"{self.visit_type} - {self.patient.full_name} ({timezone.localtime(self.visit_date):%Y-%m-%d})"

    @property
    def is_signed(self):
        return self.status == self.Status.SIGNED

    def sign(self, user, when=None):
        if self.is_signed:
            raise ValueError("This visit note is already signed.")
        self.status = self.Status.SIGNED
        self.signed_by = user
        self.signed_at = when or timezone.now()
        self.save(update_fields=["status", "signed_by", "signed_at", "updated_at"])

    @property
    def bmi(self):
        if self.weight_lb and self.height_in:
            return round(float(self.weight_lb) / float(self.height_in) ** 2 * 703, 1)
        return None


class LabResult(models.Model):
    class Flag(models.TextChoices):
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        LOW = "low", "Low"
        ABNORMAL = "abnormal", "Abnormal"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="lab_results")
    ordered_by = models.ForeignKey(
        Provider, null=True, blank=True, on_delete=models.SET_NULL, related_name="ordered_labs"
    )
    panel = models.CharField(max_length=80, blank=True)
    test_name = models.CharField(max_length=120)
    value = models.CharField(max_length=40)
    unit = models.CharField(max_length=20, blank=True)
    reference_range = models.CharField(max_length=40, blank=True)
    flag = models.CharField(max_length=10, choices=Flag.choices, default=Flag.NORMAL)
    collected_on = models.DateField()
    resulted_on = models.DateField(null=True, blank=True)
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-collected_on", "panel", "test_name"]

    def __str__(self):
        return f"{self.test_name}: {self.value} {self.unit}".strip()

    @property
    def is_abnormal(self):
        return self.flag != self.Flag.NORMAL


# ---------------------------------------------------------------------------
# Front-office workflow
# ---------------------------------------------------------------------------


class AppointmentRequest(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under review"
        SCHEDULED = "scheduled", "Scheduled"
        DECLINED = "declined", "Declined"

    OPEN_STATUSES = (Status.SUBMITTED, Status.UNDER_REVIEW)

    class Source(models.TextChoices):
        WEBSITE = "website", "Website"
        PORTAL = "portal", "Patient portal"
        PHONE = "phone", "Phone"

    reference = models.CharField(max_length=12, unique=True, editable=False)
    patient = models.ForeignKey(
        Patient, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointment_requests"
    )
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    date_of_birth = models.DateField()
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_new_patient = models.BooleanField(default=True)
    insurance_plan = models.ForeignKey(
        InsurancePlan, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointment_requests"
    )
    insurance_other = models.CharField("Other insurance", max_length=120, blank=True)
    preferred_specialty = models.ForeignKey(
        Specialty, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointment_requests"
    )
    preferred_provider = models.ForeignKey(
        Provider, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointment_requests"
    )
    preferred_office = models.ForeignKey(
        Office, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointment_requests"
    )
    preferred_times = models.CharField(max_length=200, blank=True)
    reason = models.TextField()
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.WEBSITE)
    status = models.CharField(max_length=14, choices=Status.choices, default=Status.SUBMITTED)
    staff_notes = models.TextField(blank=True)
    decline_reason = models.TextField(blank=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    appointment = models.OneToOneField(
        Appointment, null=True, blank=True, on_delete=models.SET_NULL, related_name="source_request"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} {self.full_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                candidate = f"AR-{secrets.token_hex(3).upper()}"
                if not AppointmentRequest.objects.filter(reference=candidate).exists():
                    self.reference = candidate
                    break
        super().save(*args, **kwargs)


class MessageThread(models.Model):
    """A secure-message conversation between a patient and the practice."""

    class Category(models.TextChoices):
        APPOINTMENTS = "appointments", "Appointments and scheduling"
        BILLING = "billing", "Billing and insurance"
        RECORDS = "records", "Records and forms"
        PRESCRIPTION = "prescription", "Prescription refill"
        TEST_RESULTS = "test_results", "Test results"
        CLINICAL = "clinical", "Medical question"

    class Queue(models.TextChoices):
        FRONT_OFFICE = "front_office", "Front office"
        CLINICAL = "clinical", "Care team"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    FRONT_OFFICE_CATEGORIES = (Category.APPOINTMENTS, Category.BILLING, Category.RECORDS)

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="message_threads")
    subject = models.CharField(max_length=160)
    category = models.CharField(max_length=14, choices=Category.choices)
    queue = models.CharField(max_length=14, choices=Queue.choices)
    assigned_provider = models.ForeignKey(
        Provider, null=True, blank=True, on_delete=models.SET_NULL, related_name="message_threads"
    )
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.OPEN)
    patient_has_unread = models.BooleanField(default=False)
    staff_has_unread = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.subject} ({self.patient.full_name})"

    @classmethod
    def queue_for_category(cls, category):
        return cls.Queue.FRONT_OFFICE if category in cls.FRONT_OFFICE_CATEGORIES else cls.Queue.CLINICAL

    def route(self):
        """Set the queue and, for clinical messages, the responsible provider."""
        self.queue = self.queue_for_category(self.category)
        if self.queue == self.Queue.CLINICAL:
            self.assigned_provider = self.patient.primary_provider
        else:
            self.assigned_provider = None

    @property
    def last_message(self):
        return self.messages.order_by("-created_at").first()

    @property
    def awaiting_practice_reply(self):
        last = self.last_message
        return self.status == self.Status.OPEN and last is not None and last.from_patient


class Message(models.Model):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    sender_name = models.CharField(max_length=120)
    from_patient = models.BooleanField(default=False)
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender_name}: {self.body[:40]}"


# ---------------------------------------------------------------------------
# Practice content
# ---------------------------------------------------------------------------


class PolicyDocument(models.Model):
    class Category(models.TextChoices):
        PATIENT_POLICY = "patient_policy", "Patient policies"
        BILLING = "billing", "Billing and insurance"
        VISIT_PREPARATION = "visit_preparation", "Preparing for your visit"
        PRIVACY = "privacy", "Privacy"

    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    summary = models.CharField(max_length=300)
    body = models.TextField(help_text="Plain text. Lines starting with '## ' are headings; '- ' are bullets.")
    effective_date = models.DateField()
    display_order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("public:resource_detail", args=[self.slug])
