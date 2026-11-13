from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from intranet.models import Ot
# Create your models here.


class Evento(models.Model):
    """Eventos"""
    ESTADO = [
        ('Activo', 'Activo'),
        ('Completo', 'Completo')
    ]

    TIPO = [
        ('Reunion', 'Reunión'),
        ('Llamar', 'Llamar'),
        ('Correo electrónico', 'Correo electrónico')
    ]

    titulo = models.CharField(max_length=255)
    inicio = models.DateTimeField()
    fin = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(
        choices=ESTADO, default='Activo', max_length=100, blank=True, null=True)
    ot = models.ForeignKey(Ot, on_delete=models.CASCADE, blank=True, null=True)
    allday = models.BooleanField(default=False)
    tipo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    participantes = models.ManyToManyField(
        User, related_name="eventos_participados", blank=True)

    def __str__(self):
        return f"{self.inicio} - {self.ot}"


class Recordatorio(models.Model):
    """Recordatorios"""
    UNIDAD = [
        ('minutos', 'Minutos'),
        ('horas', 'Horas'),
        ('dias', 'Días'),
    ]
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    unidad = models.CharField(max_length=10, choices=UNIDAD, default='minutos')

    def __str__(self):
        return f"Recordatorio {self.evento}"

    @property
    def minutos_antes(self):
        """Convierte todo a minutos para calcular"""
        if self.unidad == 'minutos':
            return self.cantidad
        elif self.unidad == 'horas':
            return self.cantidad * 60
        elif self.unidad == 'dias':
            return self.cantidad * 1440

    @property
    def momento_notificacion(self):
        return self.evento.inicio - timedelta(minutes=self.minutos_antes)
