"""Form helpers shared across the application."""

import datetime

from django import forms
from django.utils import timezone


class StyledFormMixin:
    """Add consistent CSS classes so templates can render fields generically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
                continue
            css = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{css} input".strip()


class DateInput(forms.DateInput):
    input_type = "date"


def validate_birth_date(value):
    today = timezone.localdate()
    if value > today:
        raise forms.ValidationError("Date of birth cannot be in the future.")
    if value < today - datetime.timedelta(days=365 * 120):
        raise forms.ValidationError("Please check the date of birth.")
    return value
