from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """A durable record of security events and patient-data access.

    Request-level logs go to log files; this table records *who did what to
    which record*, which is what a medical practice must be able to answer.
    """

    class Action(models.TextChoices):
        LOGIN = "login", "Signed in"
        LOGOUT = "logout", "Signed out"
        LOGIN_FAILED = "login_failed", "Failed sign-in"
        ACCESS_DENIED = "access_denied", "Access denied"
        VIEW_CHART = "view_chart", "Viewed patient chart"
        VIEW_PATIENT_PROFILE = "view_patient_profile", "Viewed patient profile"
        VIEW_OWN_RECORD = "view_own_record", "Patient viewed own record"
        VIEW_VISIT = "view_visit", "Viewed visit note"
        CREATE_APPOINTMENT_REQUEST = "create_appointment_request", "Submitted appointment request"
        UPDATE_APPOINTMENT_REQUEST = "update_appointment_request", "Updated appointment request"
        DECLINE_APPOINTMENT_REQUEST = "decline_appointment_request", "Declined appointment request"
        REGISTER_PATIENT = "register_patient", "Registered new patient"
        SCHEDULE_APPOINTMENT = "schedule_appointment", "Scheduled appointment"
        CANCEL_APPOINTMENT = "cancel_appointment", "Cancelled appointment"
        CHECK_IN = "check_in", "Checked in patient"
        MARK_NO_SHOW = "mark_no_show", "Marked no-show"
        SEND_MESSAGE = "send_message", "Sent message"
        CLOSE_THREAD = "close_thread", "Closed message thread"
        SAVE_VISIT_NOTE = "save_visit_note", "Saved visit note"
        SIGN_VISIT_NOTE = "sign_visit_note", "Signed visit note"

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_events"
    )
    username = models.CharField(max_length=150, blank=True, help_text="Username at the time of the event.")
    role = models.CharField(max_length=20, blank=True)
    action = models.CharField(max_length=40, choices=Action.choices, db_index=True)
    patient = models.ForeignKey(
        "clinic.Patient", null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_events"
    )
    object_type = models.CharField(max_length=60, blank=True)
    object_id = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_id = models.CharField(max_length=32, blank=True)
    path = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "audit event"

    def __str__(self):
        who = self.username or "anonymous"
        return f"{self.timestamp:%Y-%m-%d %H:%M:%S} {who} {self.action}"
