from django.db import models

from intranet.models import Ot

# Create your models here.


class Expediente(models.Model):
    """Seguimiento de Expediente"""
    ENTIDAD = [
        ('Enel', 'Enel'),
        ('Municipal', 'Municipal'),
        ('Notarial', 'Notarial'),
        ('Sedapal', 'Sedapal'),
        ('Sunarp', 'Sunarp'),
        ('Privado', 'Privado'),
    ]

    OFICINAS_SUNARP = [
        ('LIMA', 'LIMA'),
        ('ABANCAY', 'ABANCAY'),
        ('ANDAHUAYLAS', 'ANDAHUAYLAS'),
        ('AREQUIPA', 'AREQUIPA'),
        ('AYACUCHO', 'AYACUCHO'),
        ('BAGUA', 'BAGUA'),
        ('BARRANCA', 'BARRANCA'),
        ('CAJAMARCA', 'CAJAMARCA'),
        ('CALLAO', 'CALLAO'),
        ('CAMANA', 'CAMANA'),
        ('CASMA', 'CASMA'),
        ('CASTILLA _ APLAO', 'CASTILLA _ APLAO'),
        ('CAÑETE', 'CAÑETE'),
        ('CHACHAPOYAS', 'CHACHAPOYAS'),
        ('CHEPEN', 'CHEPEN'),
        ('CHICLAYO', 'CHICLAYO'),
        ('CHIMBOTE', 'CHIMBOTE'),
        ('CHINCHA', 'CHINCHA'),
        ('CHOTA', 'CHOTA'),
        ('CUSCO', 'CUSCO'),
        ('ESPINAR', 'ESPINAR'),
        ('HUACHO', 'HUACHO'),
        ('HUAMACHUCO', 'HUAMACHUCO'),
        ('HUANCAVELICA', 'HUANCAVELICA'),
        ('HUANCAYO', 'HUANCAYO'),
        ('HUANTA', 'HUANTA'),
        ('HUANUCO', 'HUANUCO'),
        ('HUARAL', 'HUARAL'),
        ('HUARAZ', 'HUARAZ'),
        ('ICA', 'ICA'),
        ('ILO', 'ILO'),
        ('ISLAY _ MOLLENDO', 'ISLAY _ MOLLENDO'),
        ('JAEN', 'JAEN'),
        ('JUANJUI', 'JUANJUI'),
        ('JULIACA', 'JULIACA'),
        ('LA MERCED (SELVA CENTRAL)', 'LA MERCED (SELVA CENTRAL)'),
        ('MADRE DE DIOS', 'MADRE DE DIOS'),
        ('MAYNAS', 'MAYNAS'),
        ('MOQUEGUA', 'MOQUEGUA'),
        ('MOYOBAMBA', 'MOYOBAMBA'),
        ('NAZCA', 'NAZCA'),
        ('OTUZCO', 'OTUZCO'),
        ('PASCO', 'PASCO'),
        ('PISCO', 'PISCO'),
        ('PIURA', 'PIURA'),
        ('PUCALLPA', 'PUCALLPA'),
        ('PUNO', 'PUNO'),
        ('QUILLABAMBA', 'QUILLABAMBA'),
        ('SAN PEDRO', 'SAN PEDRO'),
        ('SATIPO', 'SATIPO'),
        ('SICUANI', 'SICUANI'),
        ('SULLANA', 'SULLANA'),
        ('TACNA', 'TACNA'),
        ('TARAPOTO', 'TARAPOTO'),
        ('TARMA', 'TARMA'),
        ('TINGO MARIA', 'TINGO MARIA'),
        ('TRUJILLO', 'TRUJILLO'),
        ('TUMBES', 'TUMBES'),
        ('YURIMAGUAS', 'YURIMAGUAS'),
    ]

    ESTADO = [
        ('En proceso', 'En proceso'),
        ('Presentado', 'Presentado'),
        ('Reingresado', 'Reingresado'),
        ('Apelado', 'Apelado'),
        ('En calificación', 'En calificación'),
        ('Inscrito', 'Inscrito'),
        ('Reservado', 'Reservado'),
        ('Distribuido', 'Distribuido'),
        ('Liquidado', 'Liquidado'),
        ('Prorrogado', 'Prorrogado'),
        ('Observado', 'Observado'),
        ('Suspendido', 'Suspendido'),
        ('Tachado', 'Tachado'),
        ('Res. Tribunal', 'Res. Tribunal'),
        ('Res. Procedente', 'Res. Procedente'),
        ('Res. Improcedente', 'Res. Improcedente'),
        ('Anotado', 'Anotado'),
        ('Finalizado', 'Finalizado'),
        ('Entregado al Cliente', 'Entregado al Cliente'),
    ]

    ot = models.ForeignKey(Ot, on_delete=models.SET_NULL,
                           blank=True, null=True)
    entidad = models.CharField(
        max_length=45, choices=ENTIDAD, blank=True, null=True)
    oficina = models.CharField(
        max_length=50, choices=OFICINAS_SUNARP, default='LIMA', blank=True, null=True)
    numero = models.CharField(max_length=11, blank=True, null=True)
    estado = models.CharField(
        max_length=45, choices=ESTADO, blank=True, null=True)
    presentante = models.CharField(max_length=100, blank=True, null=True)
    presentacion = models.DateField(blank=True, null=True)
    reingreso = models.DateField(blank=True, null=True)
    vencimiento = models.DateField(blank=True, null=True)
    estado_devo = models.CharField(max_length=100, blank=True, null=True)
    monto_devo = models.DecimalField(
        blank=True, null=True, max_digits=8, decimal_places=2)
    creado = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)

    # NUEVOS CAMPOS PARA EL ROBOT
    actualizado_robot = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        presentacion_year = self.presentacion.strftime(
            "%Y") if self.presentacion is not None else ""
        return str(presentacion_year) + ' - ' + str(self.numero)

    ESTADOS = {
        "En proceso": "#b4b4b4",
        "Presentado": "#00a7a4",
        "Reingresado": "#1d58b4",
        "Apelado": "#ef8e00",
        "En calificación": "#5a2071",
        "Inscrito": "#89be21",
        "Reservado": "#575756",
        "Distribuido": "#f31c53",
        "Liquidado": "#006633",
        "Prorrogado": "#80d0ff",
        "Observado": "red",
        "Suspendido": "#981622",
        "Tachado": "black",
        "Res. Tribunal": "black",
        "Res. Procedente": "#006633",
        "Res. Improcedente": "black",
        "Anotado": "#7eb3d5",
        "Finalizado": "#89be21",
        "Entregado al Cliente": "#89be21",
    }

    @classmethod
    def get_color(cls, estado):
        """Color asociado a un estado"""
        return cls.ESTADOS.get(estado, "#FFFFFF")  # Color por defecto: blanco

    @classmethod
    def get_choices(cls):
        """Estados de un expediente"""
        return [(key, key) for key in cls.ESTADOS.keys()]


class ExpedienteActo(models.Model):
    """Almacena los actos y las partidas afectadas (lstTitulo)"""
    expediente = models.ForeignKey(
        Expediente, on_delete=models.CASCADE, related_name='actos'
    )
    partida_matriz = models.CharField(max_length=20)
    cod_acto = models.CharField(max_length=10)
    acto_registral = models.CharField(max_length=255)

    def __str__(self):
        return f"Partida {self.partida_matriz} - {self.acto_registral}"


class ExpedientePago(models.Model):
    """Almacena los recibos asociados al expediente (lstPagos)"""
    expediente = models.ForeignKey(
        Expediente, on_delete=models.CASCADE, related_name='pagos'
    )
    numero_recibo = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField()
    sede = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Recibo {self.numero_recibo} - S/. {self.monto}"

# ==============================================================================
# HISTORIAL DE CAMBIOS (PARA LAS NOTIFICACIONES DEL ROBOT)
# ==============================================================================


class HistorialSunarp(models.Model):
    """
    Guarda los cambios detectados por el robot de escritorio.
    """
    # db_constraint=False evita el error 150/1050 en tablas managed=False
    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name='historial',
        db_constraint=False
    )
    estado_anterior = models.CharField(max_length=100, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=100, null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Cambio {self.expediente}: {self.estado_anterior} -> {self.estado_nuevo}"
