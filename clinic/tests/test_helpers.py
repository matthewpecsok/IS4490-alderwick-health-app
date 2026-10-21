import datetime

from django import forms
from django.test import RequestFactory, TestCase
from django.utils import timezone

from clinic.context_processors import practice
from clinic.forms import StyledFormMixin, validate_birth_date
from clinic.templatetags.clinic_tags import avatar_variant, badge_class, simple_markdown, split_lines, status_badge


class SimpleMarkdownTests(TestCase):
    def test_headings_bullets_and_paragraphs(self):
        html = simple_markdown("Intro line one\nline two\n\n## Fees\n- $35 late\n- $50 no-show\nAfter list")
        self.assertIn("<p>Intro line one line two</p>", html)
        self.assertIn("<h3>Fees</h3>", html)
        self.assertIn("<ul>\n<li>$35 late</li>\n<li>$50 no-show</li>\n</ul>", html)
        self.assertIn("<p>After list</p>", html)

    def test_list_closed_by_heading_and_end(self):
        html = simple_markdown("- a\n## B\n- c")
        self.assertEqual(html.count("<ul>"), 2)
        self.assertEqual(html.count("</ul>"), 2)

    def test_escapes_html(self):
        html = simple_markdown("<script>alert(1)</script>")
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_empty(self):
        self.assertEqual(simple_markdown(None), "")


class BadgeTests(TestCase):
    def test_badge_class(self):
        self.assertEqual(badge_class("high"), "badge-danger")
        self.assertEqual(badge_class("signed"), "badge-success")
        self.assertEqual(badge_class("unknown"), "badge-muted")

    def test_status_badge_escapes_label(self):
        html = status_badge("open", "<b>x</b>")
        self.assertIn("badge-info", html)
        self.assertIn("&lt;b&gt;", html)
        self.assertIn("Checked in", status_badge("checked_in"))

    def test_split_lines_and_avatar_variant(self):
        self.assertEqual(split_lines("a\n\n b \n"), ["a", "b"])
        self.assertEqual(split_lines(None), [])
        self.assertEqual(avatar_variant(7), "alt-2")
        self.assertEqual(avatar_variant("x"), "")


class ContextProcessorTests(TestCase):
    def test_practice_context(self):
        context = practice(RequestFactory().get("/"))
        self.assertEqual(context["practice"]["name"], "Alderwick Family Health")
        self.assertIn("nurse_line", context["practice"])


class FormHelperTests(TestCase):
    def test_birth_date_validation(self):
        today = timezone.localdate()
        self.assertEqual(validate_birth_date(datetime.date(1990, 1, 1)), datetime.date(1990, 1, 1))
        with self.assertRaises(forms.ValidationError):
            validate_birth_date(today + datetime.timedelta(days=1))
        with self.assertRaises(forms.ValidationError):
            validate_birth_date(today.replace(year=today.year - 130))

    def test_styled_form_mixin_skips_checkboxes(self):
        class Sample(StyledFormMixin, forms.Form):
            name = forms.CharField()
            agree = forms.BooleanField()

        form = Sample()
        self.assertIn("input", form.fields["name"].widget.attrs["class"])
        self.assertNotIn("class", form.fields["agree"].widget.attrs)
