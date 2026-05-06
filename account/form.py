from django.forms import ModelForm
from django import forms
from .models import Account
from django.forms import ModelForm
from django import forms
from .models import Account

class AccountForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Account
        fields = [
            'username',
            'email',
            'password',
            'fullname',
            'dob',
            'address',
            'phone',
            'type'
        ]