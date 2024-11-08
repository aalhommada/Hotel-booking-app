# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.'
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'address')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'
        
        # Add placeholders and help text
        self.fields['phone'].widget.attrs['placeholder'] = '+1234567890'
        self.fields['phone'].help_text = 'Enter your phone number with country code'
        self.fields['address'].widget = forms.Textarea(attrs={
            'rows': 3,
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

class CustomUserChangeForm(UserChangeForm):
    password = None  # Remove password field from the edit form
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'address')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'
        
        # Customize the address field
        self.fields['address'].widget = forms.Textarea(attrs={
            'rows': 3,
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'
        })

class LoginForm(AuthenticationForm):  # Change to inherit from AuthenticationForm
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
        'placeholder': 'Email or Username',
        'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
        'placeholder': 'Password'
    }))
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
        })
    )