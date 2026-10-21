from django import forms

from clinic.forms import StyledFormMixin
from clinic.models import Patient


class StaffNotesForm(StyledFormMixin, forms.Form):
    staff_notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False, label="Internal notes")


class DeclineForm(StyledFormMixin, forms.Form):
    decline_reason = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), label="Reason shared with the patient", max_length=1000
    )


class ReplyForm(StyledFormMixin, forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), label="Reply to patient", max_length=4000)


class CancelForm(StyledFormMixin, forms.Form):
    reason = forms.CharField(max_length=255, label="Cancellation reason")


class NewPatientDetailsForm(StyledFormMixin, forms.Form):
    """Details needed to register a new patient when scheduling a request."""

    sex = forms.ChoiceField(choices=Patient.Sex.choices)
