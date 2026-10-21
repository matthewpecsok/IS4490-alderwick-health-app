import os
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from clinic import gemini


@override_settings(DEBUG=True)
class GeminiCheckPageTests(TestCase):
    url = reverse("devtools:gemini_check")

    def test_hidden_when_debug_is_off(self):
        with self.settings(DEBUG=False):
            self.assertEqual(self.client.get(self.url).status_code, 404)

    @mock.patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False)
    def test_shows_missing_key(self):
        response = self.client.get(self.url)
        self.assertContains(response, "not set")

    @mock.patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-1234"}, clear=False)
    def test_shows_key_hint_without_revealing_key(self):
        response = self.client.get(self.url)
        self.assertContains(response, "ends in ...1234")
        self.assertNotContains(response, "test-key-1234")

    @mock.patch("clinic.gemini.generate_text", return_value="Message received.")
    def test_post_shows_reply(self, generate_text):
        response = self.client.post(self.url, {"prompt": "Hello"})
        generate_text.assert_called_once_with("Hello")
        self.assertContains(response, "It works.")
        self.assertContains(response, "Message received.")

    @mock.patch("clinic.gemini.generate_text", side_effect=gemini.GeminiError("PermissionDenied: bad key"))
    def test_post_shows_error(self, generate_text):
        response = self.client.post(self.url, {"prompt": "Hello"})
        self.assertContains(response, "Request failed")
        self.assertContains(response, "PermissionDenied: bad key")


class GeminiClientTests(TestCase):
    @mock.patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}, clear=False)
    def test_missing_key_raises(self):
        with self.assertRaises(gemini.GeminiError):
            gemini.generate_text("Hello")

    @mock.patch.dict(os.environ, {"GEMINI_API_KEY": "k", "GEMINI_MODEL": "test-model"}, clear=False)
    @mock.patch("clinic.gemini.genai.Client")
    def test_generate_text_returns_reply(self, client_class):
        client_class.return_value.models.generate_content.return_value = mock.Mock(text="Hi there")
        self.assertEqual(gemini.generate_text("Hello"), "Hi there")
        client_class.return_value.models.generate_content.assert_called_once_with(
            model="test-model", contents="Hello", config=None
        )

    @mock.patch.dict(os.environ, {"GEMINI_API_KEY": "k"}, clear=False)
    @mock.patch("clinic.gemini.genai.Client")
    def test_api_failure_raises_gemini_error(self, client_class):
        client_class.return_value.models.generate_content.side_effect = RuntimeError("boom")
        with self.assertRaises(gemini.GeminiError):
            gemini.generate_text("Hello")
