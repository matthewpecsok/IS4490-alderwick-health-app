from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "username", "role", "action", "patient", "object_type", "object_id", "ip_address")
    list_filter = ("action", "role")
    search_fields = ("username", "patient__mrn", "patient__last_name", "request_id")
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
