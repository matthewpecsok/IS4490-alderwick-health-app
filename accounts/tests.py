from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.decorators import role_required
from accounts.models import User
from audit.models import AuditLog
from clinic.testing import PASSWORD, make_user


class UserModelTests(TestCase):
    def test_home_url_for_each_role(self):
        expected = {
            User.Role.PATIENT: reverse("portal:dashboard"),
            User.Role.FRONT_OFFICE: reverse("frontdesk:dashboard"),
            User.Role.DOCTOR: reverse("clinician:dashboard"),
            User.Role.AI_ENGINEER: reverse("aiops:index"),
            User.Role.ADMIN: reverse("admin:index"),
        }
        for role, url in expected.items():
            with self.subTest(role=role):
                self.assertEqual(make_user(role).home_url(), url)

    def test_role_properties(self):
        self.assertTrue(make_user(User.Role.PATIENT).is_patient)
        self.assertTrue(make_user(User.Role.FRONT_OFFICE).is_front_office)
        self.assertTrue(make_user(User.Role.DOCTOR).is_doctor)
        self.assertTrue(make_user(User.Role.AI_ENGINEER).is_ai_engineer)
        self.assertFalse(make_user(User.Role.DOCTOR).is_patient)

    def test_default_role_is_admin(self):
        user = User.objects.create_user(username="plain", password=PASSWORD)
        self.assertEqual(user.role, User.Role.ADMIN)

    def test_display_name_falls_back_to_username(self):
        user = make_user(User.Role.PATIENT, first_name="", last_name="")
        self.assertEqual(user.display_name, user.username)
        named = make_user(User.Role.PATIENT, first_name="Ada", last_name="Lovelace")
        self.assertEqual(named.display_name, "Ada Lovelace")


class SignInTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in")

    def test_successful_login_routes_to_role_home(self):
        cases = [
            (User.Role.PATIENT, "portal:dashboard"),
            (User.Role.FRONT_OFFICE, "frontdesk:dashboard"),
            (User.Role.DOCTOR, "clinician:dashboard"),
            (User.Role.AI_ENGINEER, "aiops:index"),
        ]
        for role, url_name in cases:
            with self.subTest(role=role):
                user = make_user(role)
                response = self.client.post(
                    reverse("accounts:login"), {"username": user.username, "password": PASSWORD}
                )
                self.assertRedirects(response, reverse("accounts:home"), fetch_redirect_response=False)
                home = self.client.get(reverse("accounts:home"))
                self.assertRedirects(home, reverse(url_name), fetch_redirect_response=False)
                self.client.logout()

    def test_bad_password_shows_error(self):
        user = make_user(User.Role.PATIENT)
        response = self.client.post(reverse("accounts:login"), {"username": user.username, "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")

    def test_signed_in_user_is_redirected_away_from_login(self):
        user = make_user(User.Role.PATIENT)
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 302)

    def test_home_requires_login(self):
        response = self.client.get(reverse("accounts:home"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:home')}")

    def test_logout_requires_post_and_redirects_home(self):
        user = make_user(User.Role.PATIENT)
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("public:home"))


class RoleRequiredTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        @role_required(User.Role.DOCTOR)
        def view(request):
            return HttpResponse("ok")

        self.view = view

    def _request(self, user=None):
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/staff/thing/")
        request.user = user or AnonymousUser()
        return request

    def test_anonymous_user_is_sent_to_login(self):
        response = self.view(self._request())
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])
        self.assertIn("next=/staff/thing/", response["Location"])

    def test_wrong_role_is_denied_and_audited(self):
        user = make_user(User.Role.PATIENT)
        with self.assertRaises(PermissionDenied):
            self.view(self._request(user))
        event = AuditLog.objects.get(action=AuditLog.Action.ACCESS_DENIED)
        self.assertEqual(event.user, user)
        self.assertEqual(event.path, "/staff/thing/")

    def test_correct_role_passes(self):
        response = self.view(self._request(make_user(User.Role.DOCTOR)))
        self.assertEqual(response.content, b"ok")
