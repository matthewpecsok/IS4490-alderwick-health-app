from django import forms

from clinic.forms import StyledFormMixin
from clinic.models import AppointmentRequest, MessageThread, Office, Provider, Specialty


class PortalAppointmentRequestForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AppointmentRequest
        fields = ["preferred_specialty", "preferred_provider", "preferred_office", "preferred_times", "reason"]
        labels = {
            "preferred_specialty": "Type of care",
            "preferred_provider": "Preferred provider",
            "preferred_office": "Preferred location",
            "preferred_times": "Days and times that work for you",
            "reason": "Reason for visit",
        }
        widgets = {"reason": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_specialty"].queryset = Specialty.objects.all()
        self.fields["preferred_specialty"].empty_label = "Not sure"
        self.fields["preferred_provider"].queryset = Provider.objects.filter(is_active=True)
        self.fields["preferred_provider"].empty_label = "No preference"
        self.fields["preferred_office"].queryset = Office.objects.all()
        self.fields["preferred_office"].empty_label = "No preference"
        self.fields["reason"].required = True


class NewMessageForm(StyledFormMixin, forms.Form):
    category = forms.ChoiceField(choices=MessageThread.Category.choices, label="What is this about?")
    subject = forms.CharField(max_length=160)
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}), label="Message", max_length=4000)


class ReplyForm(StyledFormMixin, forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), label="Reply", max_length=4000)


class CancelAppointmentForm(StyledFormMixin, forms.Form):
    reason = forms.CharField(max_length=255, required=False, label="Reason (optional)")
