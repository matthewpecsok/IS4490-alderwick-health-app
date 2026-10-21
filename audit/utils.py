import logging

from .models import AuditLog

audit_logger = logging.getLogger("alderwick.audit")


def client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_event(request, action, *, patient=None, target=None, user=None, **details):
    """Record an audit event in the database and in the audit log file.

    ``target`` is any model instance the action applies to. ``details`` must be
    JSON-serializable and should never contain clinical content.
    """
    if user is None and request is not None:
        request_user = getattr(request, "user", None)
        if request_user is not None and request_user.is_authenticated:
            user = request_user

    path = details.pop("path", None) or (request.path if request is not None else "")
    event = AuditLog.objects.create(
        user=user,
        username=details.pop("username", None) or (user.username if user else ""),
        role=getattr(user, "role", "") if user else "",
        action=action,
        patient=patient,
        object_type=target.__class__.__name__ if target is not None else "",
        object_id=str(target.pk) if target is not None else "",
        ip_address=client_ip(request),
        request_id=getattr(request, "request_id", "") if request is not None else "",
        path=path[:255],
        details=details,
    )
    audit_logger.info(
        "action=%s user=%s role=%s patient=%s object=%s:%s request_id=%s",
        event.action,
        event.username or "-",
        event.role or "-",
        patient.mrn if patient is not None else "-",
        event.object_type or "-",
        event.object_id or "-",
        event.request_id or "-",
    )
    return event
