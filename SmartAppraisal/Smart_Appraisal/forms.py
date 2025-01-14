from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    # Add fields for name, department, designation, etc., if needed during registration
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    # Change 'username' to 'email' for login authentication
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))

    # Clean the email to ensure it's properly validated
    def clean_username(self):
        email = self.cleaned_data.get('username')
        if not email:
            raise forms.ValidationError("This field is required.")
        return email
