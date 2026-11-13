"""Formularios"""
from django import forms


class OtForm(forms.Form):
    """Formulario para crear OTs"""
    nombre = forms.CharField(
        max_length=125, widget=forms.TextInput(attrs={"class": "form-control", "id": "txtNombre"}))
    descripcion = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control", "id": "txtDescripcion", "rows": "2"}))
