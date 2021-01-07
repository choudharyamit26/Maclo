from django import forms
from django.contrib.auth.models import User
from .models import UserNotification


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ['email', 'password', 'remember_me']


class UserNotificationForm(forms.ModelForm):
    class Meta:
        model = UserNotification
        fields = ('to', 'body')
