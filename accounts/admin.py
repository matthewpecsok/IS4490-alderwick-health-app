from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AlderwickUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "role", "job_title", "office", "is_active")
    list_filter = ("role", "office", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Alderwick", {"fields": ("role", "job_title", "office")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Alderwick", {"fields": ("role", "job_title", "office")}),)
