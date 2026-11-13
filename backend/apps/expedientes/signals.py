# signals.py (en tu app)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Expediente, HistorialSunarp


@receiver(pre_save, sender=Expediente)
def capturar_estado_anterior(sender, instance, **kwargs):
    if not instance.pk:
        # Si no tiene ID, es un objeto nuevo (created=True), no hay estado anterior
        instance._estado_anterior = None
    else:
        try:
            # Consultamos la BD para ver el estado antes de que se sobrescriba
            estado_viejo = sender.objects.get(pk=instance.pk).estado
            instance._estado_anterior = estado_viejo
        except sender.DoesNotExist:
            instance._estado_anterior = None

# 2. ENVIAR LA NOTIFICACIÓN SOLO SI HUBO CAMBIO


@receiver(post_save, sender=Expediente)
def procesar_cambio_estado(sender, instance, created, **kwargs):
    if created:
        return

    estado_anterior = getattr(instance, '_estado_anterior', None)

    # Verificamos si el estado realmente cambió
    if estado_anterior != instance.estado:

        # A) Guardar en el HistorialSunarp
        HistorialSunarp.objects.create(
            expediente=instance,
            estado_anterior=estado_anterior,
            estado_nuevo=instance.estado
        )

        # B) Evaluar si se envía la notificación por WebSocket
        estados_ignorados = ["En calificación",
                             "Distribuido", "Reingresado", "En proceso"]

        if instance.estado not in estados_ignorados:
            channel_layer = get_channel_layer()
            group_name = "global_notifications"

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send.notification",
                    "data": {
                        "tipo": "actualizacion_expediente",
                        "expediente_id": instance.id,
                        "numero": instance.numero,
                        "estado": instance.estado,
                        "color": Expediente.get_color(instance.estado),
                        "entidad": instance.entidad,
                        "ot_id": instance.ot_id,
                    }
                }
            )
