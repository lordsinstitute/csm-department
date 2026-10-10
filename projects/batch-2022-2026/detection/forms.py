from django import forms
from images.models import RetinaImage

class DetectionSettingsForm(forms.Form):
    confidence_threshold = forms.FloatField(
        initial=0.5,
        min_value=0.1,
        max_value=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        })
    )
    min_lesion_size = forms.IntegerField(
        initial=10,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    max_lesion_size = forms.IntegerField(
        initial=100,
        min_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )

class DetectionFilterForm(forms.Form):
    STATUS_CHOICES = (
        ('', 'All Status'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    patient = forms.ModelChoiceField(
        queryset=RetinaImage.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from django.db.models import Subquery, OuterRef
            patient_ids = RetinaImage.objects.filter(
                uploaded_by=user
            ).values_list('patient', flat=True).distinct()
            from images.models import Patient
            self.fields['patient'].queryset = Patient.objects.filter(id__in=patient_ids)