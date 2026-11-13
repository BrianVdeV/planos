"""Modelos de la aplicación intranet"""
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User


class Etiqueta(models.Model):
    """Etiquetas reutilizables"""
    COLORES = [
        ('primary',   'Primary'),
        ('secondary', 'Secondary'),
        ('success',   'Success'),
        ('danger',    'Danger'),
        ('warning',   'Warning'),
        ('info',      'Info'),
        ('dark',      'Dark'),
    ]
    nombre = models.CharField(max_length=50, unique=True)
    color = models.CharField(
        max_length=20, choices=COLORES, default='secondary')

    def __str__(self):
        return self.nombre

    def badge_html(self):
        return f'<span class="badge badge-{self.color}-lighten">{self.nombre}</span>'


class TipOt(models.Model):
    """Lista de los tipos de OT"""
    codigo = models.CharField(max_length=10)
    nom_tipo = models.CharField(max_length=255, blank=True, null=True)
    cuotas = models.IntegerField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)
    dias1 = models.IntegerField(blank=True, null=True)
    dias2 = models.IntegerField(blank=True, null=True)
    dias3 = models.IntegerField(blank=True, null=True)
    entidad = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return self.codigo


class Ot(models.Model):
    """Proyectos"""
    ESTADO_OT = [
        ('Activo', 'Activo'),
        ('Finalizado', 'Finalizado'),
        ('Suspendido', 'Suspendido'),
        ('Fallido', 'Fallido'),
    ]

    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=125)
    inicio = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(
        max_length=45, choices=ESTADO_OT, default='Activo')
    color = models.CharField(max_length=7, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    privado = models.BooleanField(default=False)
    gerente = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='gerente_ot')
    fecha_archivo = models.DateField(blank=True, null=True)
    descripcion_archivo = models.TextField(blank=True, null=True)
    id_tipot = models.ForeignKey(
        'TipOt', on_delete=models.CASCADE, null=True, blank=True, db_column='id_tipot')
    etiquetas = models.ManyToManyField('Etiqueta', blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(self.id) + ' - ' + self.nombre


class Access(models.Model):
    """Acceso a las páginas"""
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.CharField(max_length=500)
    timestamp = models.DateTimeField(default=now)
