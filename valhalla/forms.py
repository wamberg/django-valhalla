from django import forms

from valhalla import models as valhalla_models

class DeedForm(forms.ModelForm):
    """
    Used to create a valhalla.models.Deed object.
    """
    class Meta:
        model = valhalla_models.Deed
        fields = ('speaker', 'text', 'deed_date')
