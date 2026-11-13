from django import forms
from .models import Ubicacion


class UbicacionForm(forms.ModelForm):
    """Ubicacion"""
    class Meta:
        model = Ubicacion
        fields = '__all__'
