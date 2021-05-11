from django import forms
from django.contrib.auth.models import User
from .models import UserNotification, TermsCondition
from src.models import AboutUs, ContactUs


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


class UpdateAboutUsForm(forms.ModelForm):
    about_us = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = AboutUs
        fields = ('about_us',)


class UpdateContactUsForm(forms.ModelForm):
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ContactUs
        fields = ('phone_number', 'email')


class UpdateTermsConditionForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = TermsCondition
        fields = ('content',)
