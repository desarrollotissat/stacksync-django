from django import forms
from django.forms import ModelForm, PasswordInput
from users.models import StacksyncUser


class StacksyncUserForm(ModelForm):
    password = forms.CharField(widget=PasswordInput(), required=False)

    class Meta:
        model = StacksyncUser
