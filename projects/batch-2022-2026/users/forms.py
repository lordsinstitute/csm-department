from django import forms
from .models import UserRegistrationModel


class UserRegistrationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[a-zA-Z]+'}), required=True, max_length=100)
    loginid = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[a-zA-Z]+'}), required=True, max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'pattern': '(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}',
                                                                 'title': 'Must contain at least one number and one uppercase and lowercase letter, and at least 8 or more characters'}),
                               required=True, max_length=100)
    mobile = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[56789][0-9]{9}'}), required=True,
                             max_length=100)
    email = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'}),
                            required=True, max_length=100)
    locality = forms.CharField(widget=forms.TextInput(), required=True, max_length=100)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 22}), required=True, max_length=250)
    city = forms.CharField(widget=forms.TextInput(
        attrs={'autocomplete': 'off', 'pattern': '[A-Za-z ]+', 'title': 'Enter Characters Only '}), required=True,
        max_length=100)
    state = forms.CharField(widget=forms.TextInput(
        attrs={'autocomplete': 'off', 'pattern': '[A-Za-z ]+', 'title': 'Enter Characters Only '}), required=True,
        max_length=100)
    status = forms.CharField(widget=forms.HiddenInput(), initial='waiting', max_length=100)

    class Meta():
        model = UserRegistrationModel
        fields = '__all__'




# # Add this below UserRegistrationForm in the same forms.py
# from .models import TumorPrediction

# class TumorPredictionForm(forms.ModelForm):
#     class Meta:
#         model = TumorPrediction
#         fields = ['patient_name', 'uploaded_mri', 'uploaded_pet']
#         widgets = {
#             'patient_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter patient name'
#             }),
#             'uploaded_mri': forms.ClearableFileInput(attrs={
#                 'class': 'form-control'
#             }),
#             'uploaded_pet': forms.ClearableFileInput(attrs={
#                 'class': 'form-control'
#             }),
#         }
#         labels = {
#             'patient_name': 'Patient Name',
#             'uploaded_mri': 'Upload MRI Scan',
#             'uploaded_pet': 'Upload PET Scan'
#         }
