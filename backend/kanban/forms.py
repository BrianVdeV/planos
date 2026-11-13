"""Formularios Kanban"""
from django import forms
from intranet.models import User, Ot
from .models import Tarea


class TareaForm(forms.Form):
    """Formulario para crear eventos"""
    titulo = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "id": "titulo"}
        )
    )
    prioridad = forms.ChoiceField(
        choices=Tarea.PRIORITY_CHOICES, initial='low',
        widget=forms.Select(
            attrs={"class": "form-select", "id": "sltPrioridad"})
    )
    ot = forms.ModelChoiceField(
        queryset=Ot.objects.filter(estado='Activo'),
        widget=forms.Select(
            attrs={"class": "form-select", "id": "sltOt"}),
        required=False,
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        widget=forms.Select(
            attrs={"class": "form-select", "id": "sltUsuario"}),
        required=False,
    )
    descripcion = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control", "id": "txtDescripcion", "rows": "3"}), required=False)
    vencimiento = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "id": "txtVencimiento", "type": "date"}), required=False
    )
    hora = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"class": "form-control", "id": "txtHora", "type": "time"}),
        required=False
    )
    duracion = forms.CharField(
        label="Tiempo Estimado (minutos)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control-plaintext',
            'placeholder': 'minutos',
            'id': 'duracion',
            'readonly': 'readonly'
        })
    )
    responsables = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        widget=forms.SelectMultiple(
            attrs={"class": "form-select",
                   "id": "responsables", }),
        required=False,
    )


class ActividadForm(forms.Form):
    """Formulario Actividad"""
    ot = forms.ModelChoiceField(
        queryset=Ot.objects.filter(estado='Activo'),
        widget=forms.Select(
            attrs={"class": "form-select", "id": "sltOT"}),
        empty_label=None,
        required=True
    )
    tarea = forms.ModelChoiceField(
        queryset=Tarea.objects.none(),
        widget=forms.Select(
            attrs={"class": "form-select", "id": "sltTarea"}),
        required=False,
    )
    comentario = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "id": "comentario", "data-toggle": "maxlength",
                   "rows": "3", "maxlength": "150"}
        ),
        required=False,
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        widget=forms.Select(
            attrs={"class": "form-select", "id": "sltUsuario"}),
        required=False,
    )
    inicio = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"class": "form-control",
                   "id": "inicio", "type": "datetime-local"}
        )
    )
    fin = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"class": "form-control",
                   "id": "fin",  "type": "datetime-local"},),
        required=False
    )