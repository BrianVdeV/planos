from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from gastos.models import Gasto, ReporteGasto, CajaChica


@receiver(post_delete, sender=Gasto)
@receiver(post_save, sender=Gasto)
def actualizar_reporte_gasto(sender, instance, **kwargs):
    if instance.reporte:
        instance.reporte.actualizar_totales()


@receiver(post_save, sender=ReporteGasto)
def actualizar_caja_chica(sender, instance, **kwargs):
    if instance.fecha:
        caja_chica = CajaChica.objects.filter(fecha=instance.fecha).first()
        if caja_chica:
            caja_chica.save()
            caja_chica.actualizar_siguientes()
