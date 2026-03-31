from django import forms
from .models import Dataset


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ["name", "description", "file", "source_url", "status", "total_images",
                  "train_count", "val_count", "test_count"]
        widgets = {
            "name":         forms.TextInput(attrs={"class": "form-control"}),
            "description":  forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "file":         forms.FileInput(attrs={"class": "form-control"}),
            "source_url":   forms.URLInput(attrs={"class": "form-control"}),
            "status":       forms.Select(attrs={"class": "form-select"}),
            "total_images": forms.NumberInput(attrs={"class": "form-control"}),
            "train_count":  forms.NumberInput(attrs={"class": "form-control"}),
            "val_count":    forms.NumberInput(attrs={"class": "form-control"}),
            "test_count":   forms.NumberInput(attrs={"class": "form-control"}),
        }
