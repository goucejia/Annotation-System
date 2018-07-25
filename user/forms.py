from django import forms
from django.contrib.auth.models import User
from .models import File

# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('username', 'password', 'email')


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
        fields = ['path', ]  # TODO: 只上传文件，文件名自动识别

