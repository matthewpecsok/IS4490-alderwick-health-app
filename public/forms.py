from django import forms

from clinic.forms import DateInput, StyledFormMixin, validate_birth_date
from clinic.models import AppointmentRequest, InsurancePlan, Office, Provider, Specialty


class AppointmentRequestForm(StyledFormMixin, forms.ModelForm):
    acknowledge = forms.BooleanField(
        required=True,
        label="I understand this form is not for urgent or emergency needs. For emergencies I will call 911.",
    )

    class Meta:
        model = AppointmentRequest
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "email",
            "phone",
            "is_new_patient",
            "insurance_plan",
            "insurance_other",
            "preferred_specialty",
            "preferred_provider",
            "preferred_office",
            "preferred_times",
            "reason",
        ]
        labels = {
            "is_new_patient": "I have not been seen at Alderwick before",
            "insurance_plan": "Insurance plan",
            "insurance_other": "Plan not listed? Enter it here",
            "preferred_specialty": "Type of care",
            "preferred_provider": "Preferred provider (optional)",
            "preferred_office": "Preferred location (optional)",
            "preferred_times": "Days and times that work for you",
            "reason": "Reason for visit",
        }
        widgets = {
            "date_of_birth": DateInput(),
            "reason": forms.Textarea(attrs={"rows": 4}),
            "preferred_times": forms.TextInput(attrs={"placeholder": "e.g., weekday mornings"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["insurance_plan"].queryset = InsurancePlan.objects.filter(is_active=True)
        self.fields["insurance_plan"].empty_label = "Select a plan"
        self.fields["preferred_specialty"].queryset = Specialty.objects.all()
        self.fields["preferred_specialty"].empty_label = "Not sure"
        self.fields["preferred_provider"].queryset = Provider.objects.filter(is_active=True).select_related("specialty")
        self.fields["preferred_provider"].empty_label = "No preference"
        self.fields["preferred_office"].queryset = Office.objects.all()
        self.fields["preferred_office"].empty_label = "No preference"
        self.fields["reason"].required = True

    def clean_date_of_birth(self):
        return validate_birth_date(self.cleaned_data["date_of_birth"])

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("email") and not cleaned.get("phone"):
            raise forms.ValidationError("Please give us an email address or phone number so we can reach you.")
        if not cleaned.get("insurance_plan") and not cleaned.get("insurance_other"):
            self.add_error("insurance_plan", "Choose your plan, choose Self-pay, or enter your plan name below.")
        return cleaned
