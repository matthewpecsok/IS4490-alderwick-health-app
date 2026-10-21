import logging
from pathlib import Path

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.models import User
from audit.admin import AuditLogAdmin
from audit.middleware import RequestLoggingMiddleware
from audit.models import AuditLog
from audit.utils import client_ip, log_event
from clinic.testing import PASSWORD, make_patient, make_provider, make_user


class LogEventTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_records_user_patient_target_and_request_details(self):
        user = make_user(User.Role.DOCTOR)
        patient = make_patient()
        request = self.factory.get("/chart/", REMOTE_ADDR="10.1.2.3")
        request.user = user
        request.request_id = "abc123"
        with self.assertLogs("alderwick.audit", level="INFO") as logs:
            event = log_event(request, AuditLog.Action.VIEW_CHART, patient=patient, target=patient, section="labs")
        self.assertEqual(event.user, user)
        self.assertEqual(event.username, user.username)
        self.assertEqual(event.role, User.Role.DOCTOR)
        self.assertEqual(event.patient, patient)
        self.assertEqual(event.object_type, "Patient")
        self.assertEqual(event.object_id, str(patient.pk))
        self.assertEqual(event.ip_address, "10.1.2.3")
        self.assertEqual(event.request_id, "abc123")
        self.assertEqual(event.path, "/chart/")
        self.assertEqual(event.details, {"section": "labs"})
        self.assertIn("action=view_chart", logs.output[0])
        self.assertIn(patient.mrn, logs.output[0])

    def test_works_without_a_request(self):
        event = log_event(None, AuditLog.Action.LOGIN_FAILED, username="ghost")
        self.assertIsNone(event.user)
        self.assertEqual(event.username, "ghost")
        self.assertEqual(event.path, "")

    def test_anonymous_request_has_no_user(self):
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/x/")
        request.user = AnonymousUser()
        event = log_event(request, AuditLog.Action.CREATE_APPOINTMENT_REQUEST)
        self.assertIsNone(event.user)
        self.assertEqual(event.role, "")

    def test_client_ip_prefers_forwarded_header(self):
        request = self.factory.get("/", HTTP_X_FORWARDED_FOR="203.0.113.9, 10.0.0.1", REMOTE_ADDR="10.0.0.2")
        self.assertEqual(client_ip(request), "203.0.113.9")
        self.assertIsNone(client_ip(None))

    def test_string_representation(self):
        event = log_event(None, AuditLog.Action.LOGOUT, username="sam")
        self.assertIn("sam logout", str(event))


class AuthSignalTests(TestCase):
    def test_login_logout_and_failure_are_audited(self):
        user = make_user(User.Role.PATIENT)
        self.client.post(reverse("accounts:login"), {"username": user.username, "password": "nope"})
        self.client.post(reverse("accounts:login"), {"username": user.username, "password": PASSWORD})
        self.client.post(reverse("accounts:logout"))
        actions = list(AuditLog.objects.order_by("timestamp", "pk").values_list("action", flat=True))
        self.assertEqual(actions, [AuditLog.Action.LOGIN_FAILED, AuditLog.Action.LOGIN, AuditLog.Action.LOGOUT])
        failed = AuditLog.objects.get(action=AuditLog.Action.LOGIN_FAILED)
        self.assertEqual(failed.username, user.username)
        self.assertIsNone(failed.user)


class RequestLoggingMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _middleware(self, response=None, exc=None):
        def get_response(request):
            if exc:
                raise exc
            return response or HttpResponse("ok")

        return RequestLoggingMiddleware(get_response)

    def test_assigns_request_id_and_logs_request(self):
        request = self.factory.get("/providers/")
        request.user = make_user(User.Role.FRONT_OFFICE)
        with self.assertLogs("alderwick.requests", level="INFO") as logs:
            response = self._middleware()(request)
        self.assertTrue(response["X-Request-ID"])
        self.assertEqual(response["X-Request-ID"], request.request_id)
        line = logs.output[0]
        self.assertIn("path=/providers/", line)
        self.assertIn("status=200", line)
        self.assertIn("role=front_office", line)
        self.assertIn("duration_ms=", line)

    def test_reuses_safe_incoming_request_id(self):
        request = self.factory.get("/", HTTP_X_REQUEST_ID="trace42")
        with self.assertLogs("alderwick.requests", level="INFO"):
            response = self._middleware()(request)
        self.assertEqual(response["X-Request-ID"], "trace42")

    def test_rejects_unsafe_incoming_request_id(self):
        request = self.factory.get("/", HTTP_X_REQUEST_ID="bad id\nwith newline")
        with self.assertLogs("alderwick.requests", level="INFO"):
            response = self._middleware()(request)
        self.assertNotEqual(response["X-Request-ID"], "bad id\nwith newline")
        self.assertRegex(response["X-Request-ID"], r"^[0-9a-f]{16}$")

    def test_server_errors_log_at_warning(self):
        request = self.factory.get("/boom/")
        with self.assertLogs("alderwick.requests", level="WARNING") as logs:
            self._middleware(HttpResponse(status=503))(request)
        self.assertIn("status=503", logs.output[0])

    def test_exceptions_are_logged_and_reraised(self):
        request = self.factory.get("/explode/")
        with self.assertLogs("alderwick.requests", level="ERROR") as logs:
            with self.assertRaises(RuntimeError):
                self._middleware(exc=RuntimeError("kaboom"))(request)
        self.assertIn("request_failed", logs.output[0])

    def test_static_files_are_not_logged(self):
        request = self.factory.get("/static/css/alderwick.css")
        logger = logging.getLogger("alderwick.requests")
        with self.assertNoLogs(logger, level="INFO"):
            self._middleware()(request)

    def test_live_response_carries_request_id_header(self):
        response = self.client.get(reverse("public:home"))
        self.assertIn("X-Request-ID", response.headers)


class AuditAdminTests(TestCase):
    def test_audit_log_is_read_only_in_admin(self):
        admin = AuditLogAdmin(AuditLog, AdminSite())
        request = RequestFactory().get("/")
        self.assertFalse(admin.has_add_permission(request))
        self.assertFalse(admin.has_change_permission(request))
        self.assertFalse(admin.has_delete_permission(request))


class LoggingConfigurationTests(TestCase):
    def test_log_files_and_loggers_are_configured(self):
        handlers = settings.LOGGING["handlers"]
        self.assertTrue(str(handlers["app_file"]["filename"]).endswith("alderwick.log"))
        self.assertTrue(str(handlers["audit_file"]["filename"]).endswith("audit.log"))
        self.assertIn("alderwick", settings.LOGGING["loggers"])
        self.assertIn("alderwick.audit", settings.LOGGING["loggers"])
        self.assertTrue(Path(settings.LOG_DIR).is_dir())

    def test_tests_never_write_to_the_project_log_directory(self):
        self.assertNotEqual(Path(settings.LOG_DIR), Path(settings.BASE_DIR) / "logs")

    def test_chart_view_writes_to_audit_log_file_handler(self):
        provider = make_provider()
        patient = make_patient(provider=provider)
        self.client.force_login(provider.user)
        with self.assertLogs("alderwick.audit", level="INFO") as logs:
            self.client.get(reverse("clinician:chart", args=[patient.pk]))
        self.assertTrue(any("action=view_chart" in line for line in logs.output))
