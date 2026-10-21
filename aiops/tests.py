from django.test import TestCase
from django.urls import reverse

from clinic.testing import make_user


class AIOperationsTests(TestCase):
    def test_ai_engineer_sees_dashboard(self):
        self.client.force_login(make_user("ai_engineer"))
        response = self.client.get(reverse("aiops:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No AI services are connected yet")

    def test_other_roles_are_denied(self):
        for role in ("patient", "front_office", "doctor"):
            with self.subTest(role=role):
                self.client.force_login(make_user(role))
                self.assertEqual(self.client.get(reverse("aiops:index")).status_code, 403)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("aiops:index"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('aiops:index')}")
