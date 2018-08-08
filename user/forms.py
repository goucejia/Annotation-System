from django import forms
from django.contrib.auth.models import User
from .models import File


class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    cellphone = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['username', 'cellphone', 'email', 'password', ]


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['path', ]

# class PasswordResetForm(forms.Form):
#     old_password = forms.CharField(widget=forms.PasswordInput)
#     new_password = forms.CharField(widget=forms.PasswordInput)
#     confirm_password = forms.CharField(widget=forms.PasswordInput)
