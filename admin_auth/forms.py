from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, help_text='Enter your first name')
    last_name = forms.CharField(max_length=30, help_text='Enter your last name')
    email = forms.EmailField(help_text='Enter your email')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
