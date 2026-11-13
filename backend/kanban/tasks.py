"""Tareas programadas"""
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import Actividad


@shared_task
def cerrar_actividades(hora, minuto):
    """Cierra las actividades al almuerzo y termino de jornada"""
    ahora = timezone.now()
    hora_cierre = ahora.replace(
        hour=hora, minute=minuto, second=0, microsecond=0)

    actividades_abiertas = Actividad.objects.filter(fin__isnull=True)
    usuarios_afectados = set(
        actividades_abiertas.values_list('user_id', flat=True))

    total_actualizadas = actividades_abiertas.update(fin=hora_cierre)

    # 3. Notificar a cada usuario por WebSocket
    channel_layer = get_channel_layer()
    for user_id in usuarios_afectados:
        if user_id:
            grupo_usuario = f"user_notifications_{user_id}"

            async_to_sync(channel_layer.group_send)(
                grupo_usuario,
                {
                    "type": "send.notification",
                    "data": {
                        "tipo": "activity-stopped",
                        "message": f"Tu actividad fue detenida automáticamente a las {hora}:{minuto:02d}."
                    }
                }
            )

    return f"Se cerraron {total_actualizadas} actividades a las {hora}:{minuto:02d}."
