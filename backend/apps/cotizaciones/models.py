"""Modelos"""
from django.contrib.auth.models import User
from django.db import models
from djmoney.models.fields import MoneyField

from intranet.models import TipOt


class Cotizacion(models.Model):
    """Cotizaciones"""
    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('plantilla', 'Plantilla'),
    ]
    nombre = models.CharField(max_length=255)
    titulo = models.CharField(max_length=255, blank=True, null=True)
    detalles = models.TextField(max_length=2550, blank=True, null=True)
    pisos = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    cliente = models.CharField(max_length=255, blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    elaboracion = models.IntegerField(blank=True, null=True)
    estado = models.CharField(
        max_length=20, choices=ESTADO, default='pendiente')
    tipo = models.ForeignKey(
        TipOt, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'Cotización {self.id} - {self.nombre}'

    def total_cuotas(self):
        """Oferta del Servicio"""
        return sum(cuota.monto.amount for cuota in self.cancelacion_set.all())


class Cancelacion(models.Model):
    """Cuotas de la cotizacion"""
    monto = MoneyField(max_digits=7, decimal_places=2, default_currency='PEN')
    descripcion = models.CharField(max_length=255)
    fecha = models.DateField()
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE)

    def __str__(self):
        return f'Cuota {self.id} - {self.monto}'
