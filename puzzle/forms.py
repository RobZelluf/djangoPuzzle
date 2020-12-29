import os
from django import forms
from django.forms import ClearableFileInput
from .models import UploadFile, UploadCategories, UploadSettings


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ['files']
        widgets = {
            "files": ClearableFileInput(attrs={"multiple": True}),
        }


class ToolForm(forms.ModelForm):
    class Meta:
        model = UploadCategories
        fields = ['categories']


class SettingsForm(forms.ModelForm):
    class Meta:
        model = UploadSettings
        fields = ['mode', 'algorithm']
