from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import AuditLog
from .utils import log_event


@receiver(user_logged_in)
def record_login(sender, request, user, **kwargs):
    log_event(request, AuditLog.Action.LOGIN, user=user)


@receiver(user_logged_out)
def record_logout(sender, request, user, **kwargs):
    if user is not None:
        log_event(request, AuditLog.Action.LOGOUT, user=user)


@receiver(user_login_failed)
def record_login_failed(sender, credentials, request=None, **kwargs):
    log_event(request, AuditLog.Action.LOGIN_FAILED, username=credentials.get("username", ""))
