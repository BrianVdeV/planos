"""Form"""
from django import forms
from .models import Cotizacion, Cancelacion


class CotizacionForm(forms.ModelForm):
    """Formulario para Cotizacion"""
    class Meta:
        """Meta"""
        model = Cotizacion
        fields = ["titulo", "cliente", "detalles", "pisos", "area",
                  "telefono", "ubicacion", "dni", "tipo"]  # o los campos que necesites
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "id": "titulo", "maxlength": 200, "required": True}),
            "dni": forms.TextInput(attrs={"class": "form-control", "id": "dni", "title": "Ingrese 8 dígitos para DNI o 11 dígitos para RUC", "maxlength": 11}),
            "cliente": forms.TextInput(attrs={"class": "form-control", "id": "cliente", "minlength": 2, "maxlength": 150, "required": True}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "id": "telefono", "title": "Ingrese un número de teléfono válido (9 dígitos, opcional +51)", "maxlength": 20}),
            "ubicacion": forms.TextInput(attrs={"class": "form-control", "id": "ubicacion", "minlength": 3, "maxlength": 200, "required": True}),
            "pisos": forms.NumberInput(attrs={"class": "form-control", "id": "pisos", "min": 1, "max": 50}),
            "area": forms.NumberInput(attrs={"class": "form-control", "id": "area", "min": 1, "max": 10000, "required": True}),
            "detalles": forms.Textarea(attrs={"class": "form-control", "id": "detalles", "rows": 3, "minlength": 10, "maxlength": 1000, "required": True}),
            "tipo": forms.Select(attrs={"class": "form-select", "required": True})
        }


class CancelacionForm(forms.ModelForm):
    """Cuotas de la cotizacion"""
    class Meta:
        """Meta"""
        model = Cancelacion
        fields = ["cotizacion", "monto", "descripcion", "fecha"]
        widgets = {
            "cotizacion": forms.Select(attrs={"class": "form-select", "id": "cotizacion", "required": True}),
            "monto": forms.NumberInput(attrs={"class": "form-control", "id": "monto", "step": "0.01", "min": "0.01", "required": True}),
            "descripcion": forms.TextInput(attrs={"class": "form-control", "id": "descripcion", "maxlength": 255, "required": True}),
            "fecha": forms.DateInput(attrs={"class": "form-control", "id": "fecha", "type": "date", "required": True}),
        }
