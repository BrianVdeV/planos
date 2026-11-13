"""Modelo para tareas en el sistema Kanban."""
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from intranet.models import User, Ot


class Tarea(models.Model):
    """Modelo para tareas en el sistema Kanban."""
    STATUS_CHOICES = [
        ('todo', 'Por Hacer'),
        ('in_progress', 'En Progreso'),
        ('review', 'En Revisión'),
        ('done', 'Hecho'),
    ]
    PRIORITY_CHOICES = [
        ('high', 'Muy Urgente'),
        ('medium', 'Urgente'),
        ('low', 'Estable'),
    ]
    responsables = models.ManyToManyField(
        User, blank=True, related_name='tareas_responsables')
    ot = models.ForeignKey(Ot, on_delete=models.CASCADE, null=True, blank=True)
    titulo = models.CharField(max_length=200, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    estado = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='todo', null=True, blank=True)
    prioridad = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='low', null=True, blank=True)
    inicio = models.DateTimeField(null=True, blank=True)
    vencimiento = models.DateTimeField(null=True, blank=True)
    finalizado = models.DateTimeField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)
    duracion = models.DurationField(null=True, blank=True)
    orden = models.PositiveIntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return self.titulo


class Actividad(models.Model):
    """Registro de actividades"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    ot = models.ForeignKey(Ot, on_delete=models.SET_NULL,
                           blank=True, null=True)
    tarea = models.ForeignKey(
        Tarea, on_delete=models.SET_NULL, blank=True, null=True)
    inicio = models.DateTimeField(default=now, blank=True, null=True)
    fin = models.DateTimeField(blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    pausado = models.BooleanField(
        default=False, help_text="True si la actividad fue pausada para continuarla luego")

    def __str__(self):
        return str(self.inicio) + ' - ' + str(self.comentario) + ' - ' + str(self.user)

    def total(self):
        """Total en horas y minutos, asegurando que el cálculo
        empieza a las 08:00 si inicio es antes de las 08:00"""
        if self.inicio and self.fin:
            # Definir las 08:00 como la hora de inicio mínima
            hora_limite = self.inicio.replace(
                hour=8, minute=0, second=0, microsecond=0)
            # Si inicio es antes de las 08:00, ajustamos inicio a las 08:00
            if self.inicio < hora_limite:
                self.inicio = hora_limite

            # Calcular la diferencia entre inicio y fin
            diferencia = self.fin - self.inicio
            horas, segundos = divmod(diferencia.total_seconds(), 3600)
            minutos = segundos // 60
            return f"{int(horas):02}:{int(minutos):02}"
        return None

    def total_decimal(self):
        """Calcula la diferencia entre inicio y fin en formato decimal,
        asegurando que el cálculo empieza a las 08:00 si inicio es antes de las 08:00"""
        if self.inicio and self.fin:
            # Definir las 08:00 como la hora de inicio mínima
            hora_limite = self.inicio.replace(
                hour=8, minute=0, second=0, microsecond=0)
            # Si inicio es antes de las 08:00, ajustamos inicio a las 08:00
            if self.inicio < hora_limite:
                # Modificamos inicio a las 08:00
                inicio_ajustada = hora_limite
            else:
                # Si inicio es después de las 08:00, usamos inicio tal como está
                inicio_ajustada = self.inicio

            # Calcular la diferencia entre inicio ajustada y fin en segundos
            diferencia = self.fin - inicio_ajustada
            horas_decimales = diferencia.total_seconds() / 3600
            return round(horas_decimales, 2)
        return None

    def get_duracion_seconds(self):
        """ Devuelve el campo duracion en segundos totales """
        if self.tarea and self.tarea.duracion:
            return int(self.tarea.duracion.total_seconds())
        return 0


@receiver(post_save, sender=Ot)
def crear_tareas(sender, instance, created, **kwargs):
    """Crear tareas automáticamente según el tipo de OT"""
    if not created:
        return

    tareas_tipo_7 = [
        "A.1 Visita - Medicion",
        "B.1 Anteproyecto",
        "B.2 Arquitectura",
        "B.3 Cortes y Elevaciones",
        "B.4 Estructuras de Cimentación",
        "B.5 Estructuras Techos Aligerados",
        "B.6 Instalaciones Electricas",
        "B.7 Instalaciones Sanitarias",
        "B.8 Instalaciones Gas Natural",
        "B.9 Instalaciones Redes",
        "B.10 ETABS",
        "B.11 Diseño 3D",
    ]

    tareas_tipo_8 = [
        "A.1 Visita - Medicion",
        "B.1 Anteproyecto",
        "B.2 Arquitectura",
        "B.3 Cortes y Elevaciones",
        "B.4 Estructuras de Cimentación",
        "B.4 Estructuras Techos Aligerados",
        "B.6 Instalaciones Electricas",
        "B.7 Instalaciones Sanitarias",
        "B.8 Instalaciones Gas Natural",
        "B.9 Instalaciones Redes",
        "B.10 Ubicación - Localización",
        "C. Documentos",
        "D.17 Servicio de Tramitación",
    ]

    tareas_otro = [
        "A.1 Visita - Medicion",
        "B.2 Arquitectura - Distribución",
        "B.10 Ubicación - Localización",
        "B.13 Perimetrico",
        "C. Documentos",
        "C.1 Lectura Título SUNARP (si fuera el caso)",
        "D.16 Servicio de Tramitación - Notaria",
        "D.17 Servicio de Tramitación - SUNARP",
    ]

    if instance.id_tipot and instance.id_tipot.id == 7:
        tareas = tareas_tipo_7
    elif instance.id_tipot and instance.id_tipot.id == 8:
        tareas = tareas_tipo_8
    else:
        tareas = tareas_otro

    for nombre_tarea in tareas:
        Tarea.objects.create(
            ot=instance,
            titulo=nombre_tarea
        )


# Receptores para marcar tareas como 'done' cuando una OT pasa a 'Finalizado'
@receiver(pre_save, sender=Ot)
def ot_pre_save(sender, instance, **kwargs):
    """Guardar el estado previo en la instancia para compararlo en post_save."""
    if instance.pk:
        try:
            prev = sender.objects.get(pk=instance.pk)
            instance._prev_estado = prev.estado
        except sender.DoesNotExist:
            instance._prev_estado = None
    else:
        instance._prev_estado = None


@receiver(post_save, sender=Ot)
def ot_post_save_mark_tareas(sender, instance, created, **kwargs):
    """Si la OT cambia a 'Finalizado', marcar todas sus tareas como done."""
    # Solo actuar si el estado actual es 'Finalizado' y antes no lo era
    if getattr(instance, 'estado', None) == 'Finalizado' and getattr(instance, '_prev_estado', None) != 'Finalizado':
        Tarea.objects.filter(ot=instance).exclude(
            estado='done').update(estado='done')


def actividad_post_save(sender, instance, created, **kwargs):
    """Al crear una Actividad, ajustar el estado de las tareas del usuario."""
    if not created:
        return

    tarea = instance.tarea
    user = instance.user

    if not tarea or not user:
        return

    otras_tareas = Tarea.objects.filter(
        responsables=user, estado__in=['todo', 'in_progress']
    ).exclude(pk=tarea.pk).distinct()

    otras_tareas.update(estado='todo')

    Tarea.objects.filter(pk=tarea.pk).update(estado='in_progress')
