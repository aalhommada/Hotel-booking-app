# accounts/forms.py
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get("phone", ""),
                address=self.cleaned_data.get("address", ""),
            )
        return user


class CustomUserChangeForm(UserChangeForm):
    password = None
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm",
            }
        ),
        required=False,
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, "profile"):
            self.fields["phone"].initial = self.instance.profile.phone
            self.fields["address"].initial = self.instance.profile.address

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get("phone", "")
            profile.address = self.cleaned_data.get("address", "")
            profile.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm",
                "placeholder": "Username or Email",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm",
                "placeholder": "Password",
            }
        )
    )
    remember_me = forms.BooleanField(required=False, initial=False)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            # Try to authenticate with email
            if "@" in username:
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                    cleaned_data["username"] = username
                except User.DoesNotExist:
                    raise forms.ValidationError("Invalid email or password")

        return cleaned_data
