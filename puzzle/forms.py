import os
from django import forms
from django.forms import ClearableFileInput
from .models import UploadFile, UploadCategories


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
