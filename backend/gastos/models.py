"""Modelo de app Gastos"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum

from intranet.models import Ot


class ReporteGasto(models.Model):
    """Reporte para con saldo total de los gastos"""
    ESTADOS_APROBACION = [
        (0, 'Sin Enviar'),
        (1, 'Pendiente'),
        (2, 'Aprobado'),
        (3, 'Rechazado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    vuelto = models.DecimalField(max_digits=10, decimal_places=2)
    estado_aprobacion = models.IntegerField(
        choices=ESTADOS_APROBACION, default=0)
    mensaje = models.TextField(blank=True, null=True)

    def actualizar_totales(self):
        """Calcula la suma de los gastos y actualiza total y vuelto."""
        total_gastos = Gasto.objects.filter(reporte=self).aggregate(Sum('monto'))[
            'monto__sum'] or 0
        self.total = total_gastos
        self.vuelto = self.monto_recibido - self.total
        self.save()

    def __str__(self):
        return f"{self.fecha} - {self.usuario} - S/. {self.total}"


class Gasto(models.Model):
    """Los gastos"""
    CATEGORIAS = [
        ('Firma', 'Firma'),
        ('Movilidad', 'Movilidad'),
        ('Municipalidad', 'Municipalidad'),
        ('Notaria', 'Notaría'),
        ('Oficina', 'Oficina'),
        ('Otros', 'Otros'),
        ('Sunarp', 'Sunarp'),
        ('Taxi', 'Taxi'),
    ]
    ot = models.ForeignKey(Ot, on_delete=models.SET_NULL,
                           null=True, blank=True)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    reporte = models.ForeignKey(
        ReporteGasto, on_delete=models.CASCADE, null=True, blank=True)
    archivo = models.FileField(upload_to='gastos/', blank=True, null=True)
    editado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ot} - S/. {self.monto}"


class Saldo(models.Model):
    """"Saldo prestado a cada usuario"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    saldo_inicial = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)  # Guarda el saldo inicial
    saldo_actual = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)   # Se va descontando
    # Guarda la fecha de creación y no cambia
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - Inicial: S / {self.saldo_inicial} - Actual: S / {self.saldo_actual}"


class CajaChica(models.Model):
    """Contabilidad diaria de la chaja chica"""
    saldo_inicial = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)  # Saldo inicial
    saldo_actual = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)  # Saldo actual
    ingreso = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)  # Ingreso
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)  # Total
    fecha = models.DateField()  # Fecha de la caja chica

    def calcular_total_reportes_gasto(self):
        """
        Suma los reportes de gasto aprobados cuya fecha coincide exactamente
        con la fecha de esta caja chica.
        """
        from decimal import Decimal
        from .models import ReporteGasto

        reportes_gasto = ReporteGasto.objects.filter(
            fecha=self.fecha,
            estado_aprobacion=2  # Solo reportes aprobados
        )

        total_gastos = sum(Decimal(reporte.total)
                           for reporte in reportes_gasto)
        return total_gastos

    def save(self, *args, **kwargs):
        # Buscar la última caja anterior, sin importar si fue viernes u otro día hábil
        caja_anterior = CajaChica.objects.filter(
            fecha__lt=self.fecha
        ).order_by('-fecha').first()

        if caja_anterior:
            self.saldo_inicial = caja_anterior.total  # Pasar total como saldo_inicial

        # Calcular saldo actual y total
        total_reportes_gasto = self.calcular_total_reportes_gasto()
        self.saldo_actual = Decimal(self.saldo_inicial) + Decimal(self.ingreso)
        self.total = self.saldo_actual - total_reportes_gasto

        super(CajaChica, self).save(*args, **kwargs)

        # 🔄 **Actualizar los registros posteriores**
        self.actualizar_siguientes()

    def actualizar_siguientes(self):
        """
        Actualiza los registros de los días siguientes si cambia el total.
        """
        cajas_siguientes = CajaChica.objects.filter(
            fecha__gt=self.fecha).order_by('fecha')

        saldo = self.total  # Nuevo saldo inicial para el siguiente día

        for caja in cajas_siguientes:
            caja.saldo_inicial = saldo
            caja.saldo_actual = caja.saldo_inicial + caja.ingreso
            caja.total = caja.saldo_actual - caja.calcular_total_reportes_gasto()

            caja.save()

            saldo = caja.total  # Pasar el nuevo total al siguiente día

    def __str__(self):
        return f'{self.fecha} - Ingreso: {self.ingreso} - Saldo: {self.saldo_actual} - Total: {self.total}'


# Función para actualizar el reporte de gasto en un hilo separado
def actualizar_reporte_gasto_async(instance):
    # Llamar a la función que actualiza los totales del reporte
    if instance.reporte:
        print(f"Actualizando ReporteGasto ID {instance.reporte.id}")
        instance.reporte.actualizar_totales()

# Función para actualizar la caja chica en un hilo separado


def actualizar_caja_chica_async(instance):
    # Llamar a la función que actualiza la CajaChica
    if instance.fecha:  # Verifica que el ReporteGasto tiene una fecha asociada
        # Encuentra la CajaChica de la misma fecha
        caja_chica = CajaChica.objects.filter(fecha=instance.fecha).first()
        if caja_chica:
            print(
                f"Actualizando CajaChica ID {caja_chica.id} debido al ReporteGasto ID {instance.id}")
            caja_chica.save()
            caja_chica.actualizar_siguientes()


def crear_cajas_chicas_faltantes():
    from .models import CajaChica
    hoy = date.today()

    if CajaChica.objects.filter(fecha=hoy).exists():
        return

    ultima_caja = CajaChica.objects.order_by('-fecha').first()
    if not ultima_caja:
        return

    # Obtener fechas ya existentes de una sola consulta
    fechas_existentes = set(CajaChica.objects.values_list('fecha', flat=True))

    fecha_actual = ultima_caja.fecha + timedelta(days=1)

    nuevas_cajas = []

    while fecha_actual <= hoy:
        if fecha_actual.weekday() < 5 and fecha_actual not in fechas_existentes:
            nuevas_cajas.append(CajaChica(fecha=fecha_actual))
        fecha_actual += timedelta(days=1)

    for caja in nuevas_cajas:
        caja.save()


class Contrato(models.Model):
    """Contratos de los trabajadores"""
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100)
    inicio = models.DateField()
    fin = models.DateField()
    sueldo = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.cargo} - {self.id_user}"

    def meses_duracion(self):
        """Duración del contrato en meses."""
        return (self.fin.year - self.inicio.year) * 12 + self.fin.month - self.inicio.month + 1
