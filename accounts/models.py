from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Application user. Every user has exactly one role that controls access."""

    class Role(models.TextChoices):
        PATIENT = "patient", "Patient"
        FRONT_OFFICE = "front_office", "Front office"
        DOCTOR = "doctor", "Doctor"
        AI_ENGINEER = "ai_engineer", "AI engineer"
        ADMIN = "admin", "Administrator"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMIN)
    job_title = models.CharField(max_length=120, blank=True)
    office = models.ForeignKey(
        "clinic.Office",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="staff_members",
        help_text="Home office for front-office staff.",
    )

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

    @property
    def is_front_office(self):
        return self.role == self.Role.FRONT_OFFICE

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_ai_engineer(self):
        return self.role == self.Role.AI_ENGINEER

    @property
    def display_name(self):
        full = self.get_full_name()
        return full or self.username

    def home_url(self):
        """Where this user lands after signing in."""
        destinations = {
            self.Role.PATIENT: "portal:dashboard",
            self.Role.FRONT_OFFICE: "frontdesk:dashboard",
            self.Role.DOCTOR: "clinician:dashboard",
            self.Role.AI_ENGINEER: "aiops:index",
            self.Role.ADMIN: "admin:index",
        }
        return reverse(destinations.get(self.role, "public:home"))
