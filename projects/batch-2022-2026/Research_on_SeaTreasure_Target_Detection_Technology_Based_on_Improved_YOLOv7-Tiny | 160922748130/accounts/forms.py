from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "class": "form-control", "placeholder": "Email Address"
    }))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "First Name"
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Last Name"
    }))
    organization = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Organization (optional)"
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Phone (optional)"
    }))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Confirm Password"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                organization=self.cleaned_data.get("organization", ""),
                phone=self.cleaned_data.get("phone", ""),
            )
        return user


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Username"})
        self.fields["password"].widget.attrs.update({"class": "form-control", "placeholder": "Password"})


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = UserProfile
        fields = ["phone", "organization", "bio", "profile_picture"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "organization": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "profile_picture": forms.FileInput(attrs={"class": "form-control"}),
        }
