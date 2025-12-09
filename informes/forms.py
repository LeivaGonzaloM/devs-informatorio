from django import forms
from .models import Informe

class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ["title", "description"]
