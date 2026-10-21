import logging
import time
import uuid

logger = logging.getLogger("alderwick.requests")

SKIP_PREFIXES = ("/static/", "/favicon.ico")


class RequestLoggingMiddleware:
    """Give every request an ID and log method, path, status, timing, and user.

    The request ID is returned in the ``X-Request-ID`` response header and is
    attached to audit events so a single request can be traced across logs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.headers.get("X-Request-ID", "")
        request.request_id = incoming[:32] if incoming.isalnum() else uuid.uuid4().hex[:16]
        started = time.monotonic()
        try:
            response = self.get_response(request)
        except Exception:
            logger.exception(
                "request_failed request_id=%s method=%s path=%s", request.request_id, request.method, request.path
            )
            raise
        duration_ms = (time.monotonic() - started) * 1000
        response["X-Request-ID"] = request.request_id

        if not request.path.startswith(SKIP_PREFIXES):
            user = getattr(request, "user", None)
            authenticated = user is not None and user.is_authenticated
            level = logging.WARNING if response.status_code >= 500 else logging.INFO
            logger.log(
                level,
                "request request_id=%s method=%s path=%s status=%s duration_ms=%.1f user=%s role=%s",
                request.request_id,
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                user.username if authenticated else "-",
                user.role if authenticated else "-",
            )
        return response
