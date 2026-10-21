from django.contrib import admin

from . import models


class OfficeHoursInline(admin.TabularInline):
    model = models.OfficeHours
    extra = 0


@admin.register(models.Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone", "is_virtual")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [OfficeHoursInline]


@admin.register(models.Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    list_display = ("name", "carrier", "plan_type", "is_active")
    list_filter = ("plan_type", "is_active")


class ProviderScheduleInline(admin.TabularInline):
    model = models.ProviderSchedule
    extra = 0


@admin.register(models.Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("display_name", "specialty", "accepting_new_patients", "offers_telehealth", "user")
    list_filter = ("specialty", "accepting_new_patients", "offers_telehealth", "offices")
    search_fields = ("first_name", "last_name")
    filter_horizontal = ("offices", "insurance_plans")
    inlines = [ProviderScheduleInline]


@admin.register(models.AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "duration_minutes", "is_telehealth")


class AllergyInline(admin.TabularInline):
    model = models.Allergy
    extra = 0


class ProblemInline(admin.TabularInline):
    model = models.Problem
    extra = 0


class MedicationInline(admin.TabularInline):
    model = models.Medication
    extra = 0


@admin.register(models.Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("mrn", "last_name", "first_name", "date_of_birth", "primary_provider", "insurance_plan", "user")
    list_filter = ("primary_office", "insurance_plan")
    search_fields = ("mrn", "first_name", "last_name", "email")
    inlines = [AllergyInline, ProblemInline, MedicationInline]


@admin.register(models.Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("start", "patient", "provider", "office", "appointment_type", "status")
    list_filter = ("status", "office", "provider")
    date_hierarchy = "start"
    search_fields = ("patient__last_name", "patient__mrn")


@admin.register(models.Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("visit_date", "patient", "provider", "visit_type", "status")
    list_filter = ("status", "provider")
    date_hierarchy = "visit_date"


@admin.register(models.LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ("collected_on", "patient", "test_name", "value", "unit", "flag")
    list_filter = ("flag", "panel")


@admin.register(models.AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ("reference", "full_name", "status", "source", "is_new_patient", "created_at")
    list_filter = ("status", "source", "is_new_patient")
    search_fields = ("reference", "first_name", "last_name")


class MessageInline(admin.TabularInline):
    model = models.Message
    extra = 0


@admin.register(models.MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ("subject", "patient", "category", "queue", "assigned_provider", "status", "updated_at")
    list_filter = ("queue", "category", "status")
    inlines = [MessageInline]


@admin.register(models.PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "effective_date", "is_public", "display_order")
    prepopulated_fields = {"slug": ("title",)}
