from django import forms

from clinic.forms import StyledFormMixin
from clinic.models import Visit


class VisitNoteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Visit
        fields = [
            "chief_complaint",
            "blood_pressure",
            "heart_rate",
            "temperature_f",
            "weight_lb",
            "height_in",
            "oxygen_saturation",
            "subjective",
            "objective",
            "assessment",
            "plan",
            "patient_instructions",
        ]
        labels = {
            "temperature_f": "Temp (F)",
            "weight_lb": "Weight (lb)",
            "height_in": "Height (in)",
            "oxygen_saturation": "SpO2 (%)",
            "heart_rate": "Heart rate",
            "patient_instructions": "After-visit summary for patient",
        }
        widgets = {
            "subjective": forms.Textarea(attrs={"rows": 5}),
            "objective": forms.Textarea(attrs={"rows": 5}),
            "assessment": forms.Textarea(attrs={"rows": 4}),
            "plan": forms.Textarea(attrs={"rows": 4}),
            "patient_instructions": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_blood_pressure(self):
        value = self.cleaned_data.get("blood_pressure", "").strip()
        if value:
            parts = value.split("/")
            if len(parts) != 2 or not all(p.strip().isdigit() for p in parts):
                raise forms.ValidationError("Enter blood pressure as systolic/diastolic, e.g. 120/80.")
        return value


class ReplyForm(StyledFormMixin, forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}), label="Reply to patient", max_length=4000)
