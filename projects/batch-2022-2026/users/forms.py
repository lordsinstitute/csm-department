from django import forms
from .models import UserProfile
import re

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'username', 'password', 'email', 'phone_number', 'address']
        widgets = {
            'password': forms.PasswordInput(),
            'address': forms.Textarea(attrs={'rows': 4}),
            'status': forms.Select(),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not re.match(r'^[a-zA-Z\s]{2,100}$', name):
            raise forms.ValidationError('Name must be 2-100 characters long and contain only letters and spaces.')
        return name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]{3,50}$', username):
            raise forms.ValidationError('Username must be 3-50 characters long and contain only letters, numbers, and underscores.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*]', password):
            raise forms.ValidationError('Password must contain at least one special character (!@#$%^&*).')
        return password

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise forms.ValidationError('Phone number must be 9-15 digits and may include a leading +.')
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError('Enter a valid email address.')
        return email

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if len(address) < 5:
            raise forms.ValidationError('Address must be at least 5 characters long.')
        return 
    
class UploadFileForm(forms.Form):
    file = forms.FileField(label='Select an image or video')