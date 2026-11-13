"""Models"""
from django.db import models
from intranet.models import Ot


class Ubigeo(models.Model):
    """Lista con los ubigeos del pais segun RENIEC o no me acuerdo"""
    id = models.AutoField(primary_key=True)
    departamento = models.CharField(max_length=255)
    provincia = models.CharField(max_length=255)
    distrito = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.departamento} - {self.provincia} - {self.distrito}"


class Ubicacion(models.Model):
    """Ubicaciones de las OTS"""
    id = models.AutoField(primary_key=True)
    ot = models.ForeignKey(
        Ot, on_delete=models.CASCADE)
    ubigeo = models.ForeignKey(Ubigeo, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=125)
    coordenadas = models.CharField(max_length=125)

    class Meta:
        ordering = ['-ot__id']

    def __str__(self):
        return f"{self.ot} - {self.direccion}"
