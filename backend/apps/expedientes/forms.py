"""Formularios"""
from django import forms
from intranet.models import Ot
from .models import Expediente


class ExpedienteForm(forms.Form):
    """Expediente"""
    ot = forms.ModelChoiceField(
        queryset=Ot.objects.filter(estado='Activo'),
        widget=forms.Select(
            attrs={"class": "form-select", "id": "ot"}),
        empty_label=None,
    )
    numero = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "id": "numero"}
        ), required=False
    )
    estado = forms.ChoiceField(
        choices=Expediente.ESTADOS,
        widget=forms.Select(
            attrs={"class": "form-select", "id": "estado"})
    )
    entidad = forms.ChoiceField(
        choices=Expediente.ENTIDAD,
        widget=forms.Select(
            attrs={"class": "form-select", "id": "entidad"})
    )
    oficina = forms.ChoiceField(
        choices=Expediente.OFICINAS_SUNARP,
        widget=forms.Select(
            attrs={"class": "form-select", "id": "oficina"}),
        required=False
    )
    presentacion = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "id": "presentacion", "type": "date"}),
        required=False
    )
    reingreso = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "id": "reingreso", "type": "date"}),
        required=False
    )
    vencimiento = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "id": "vencimiento", "type": "date"}),
        required=False
    )
