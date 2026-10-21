from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow a view only for signed-in users whose role is in ``roles``.

    Anonymous users are sent to the sign-in page. Signed-in users with the wrong
    role receive HTTP 403 and an ``access_denied`` audit event is recorded.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if request.user.role not in roles:
                from audit.models import AuditLog
                from audit.utils import log_event

                log_event(request, AuditLog.Action.ACCESS_DENIED, path=request.path)
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
