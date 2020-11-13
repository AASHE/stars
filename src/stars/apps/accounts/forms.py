from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm

from stars.apps.institutions.models import StarsAccount


class LoginForm(AuthenticationForm):
    """ Extends the AuthenticationForm to use longer usernames """

    username = forms.CharField(label="Email", max_length=100)
