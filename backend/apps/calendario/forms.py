from django import forms
from django.contrib.auth.models import User

from .models import Ot


class EventoForm(forms.Form):
    """Formulario para crear eventos"""
    titulo = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={"class": "form-control", "id": "titulo"}))
    fecha = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "id": "fecha", "type": "date"}),
        required=False
    )
    inicio = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"class": "form-control", "id": "inicio", "type": "time"}),
        required=False
    )
    fin = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"class": "form-control", "id": "fin", "type": "time"}),
        required=False
    )
    ot = forms.ModelChoiceField(
        queryset=Ot.objects.filter(estado='Activo'),
        widget=forms.Select(
            attrs={"class": "form-select", "id": "ot"}),
        required=False,
    )
    participantes = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        widget=forms.SelectMultiple(
            attrs={"class": "select2 form-control select2-multiple",
                   "data-toggle": "select2", "multiple": "multiple", "id": "participantes", }),
        required=False,
    )
    descripcion = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control", "id": "txtDescripcion", "rows": "2"}), required=False)
