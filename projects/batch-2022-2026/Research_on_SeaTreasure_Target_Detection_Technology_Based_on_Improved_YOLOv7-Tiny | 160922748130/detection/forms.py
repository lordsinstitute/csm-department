from django import forms
from .models import DetectionJob


class DetectionUploadForm(forms.ModelForm):
    class Meta:
        model = DetectionJob
        fields = ["name", "input_file", "confidence_threshold", "iou_threshold", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Detection job name (optional)"
            }),
            "input_file": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*,video/*"
            }),
            "confidence_threshold": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.05", "min": "0.1", "max": "0.95"
            }),
            "iou_threshold": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.05", "min": "0.1", "max": "0.95"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control", "rows": 2,
                "placeholder": "Optional notes..."
            }),
        }
