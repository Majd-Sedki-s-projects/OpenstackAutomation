from django import forms
from .models import NetworkApplications


class ConfigurationForm(forms.Form):
    config_file = forms.FileField(label="Select a file")

    class Meta:
        model = NetworkApplications
