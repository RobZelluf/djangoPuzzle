import os
from django import forms
from django.db import models
from django.forms import ClearableFileInput
from .models import UploadFile, UploadCategories, UploadSettings, UpdateCell


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
        fields = ['mode', 'algorithm', 'timeout', "use_self_filled", "double_check", "use_fixed"]


class UpdateCellForm(forms.ModelForm):
    answer = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        options = kwargs.pop('options')
        curr_value = kwargs.pop('curr_value', None)

        options = tuple([(x, x) for x in options])
        super(UpdateCellForm, self).__init__(*args, **kwargs)

        self.fields['answer'].choices = options
        if curr_value is not None:
            self.fields['answer'].default = curr_value

    class Meta:
        model = UpdateCell
        fields = ['answer']

