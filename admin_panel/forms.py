from django import forms
from users import models as user_models

class AddGridForm(forms.Form):
    grid = forms.ModelChoiceField(queryset=user_models.grid.objects.all(), label="Select Grid")

class RemoveGridForm(forms.Form):
    grid = forms.ModelChoiceField(queryset=user_models.grid.objects.all(), label="Select Grid")
