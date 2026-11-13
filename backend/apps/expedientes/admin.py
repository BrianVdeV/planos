from django.contrib import admin
from .models import Expediente, HistorialSunarp, ExpedienteActo, ExpedientePago


@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    """Admin para Expediente"""
    list_display = ['id', 'ot', 'entidad', 'oficina', '__str__', 'estado']
    list_filter = ['entidad', 'estado', 'oficina']

    ordering = ['-id']
    search_fields = ['id', 'ot__id', 'ot__nombre',
                     'entidad', 'oficina', 'estado', 'numero']


admin.site.register(HistorialSunarp)


@admin.register(ExpedienteActo)
class ExpedienteActoAdmin(admin.ModelAdmin):
    """Admin para ExpedienteActo"""
    list_display = ['id', 'expediente', 'acto_registral', 'partida_matriz']
    search_fields = ['expediente__id', 'expediente__numero',
                     'acto_registral', 'partida_matriz']


@admin.register(ExpedientePago)
class ExpedientePagoAdmin(admin.ModelAdmin):
    """Admin para ExpedientePago"""
    list_display = ['id', 'sede', 'expediente', 'monto', 'fecha']
    search_fields = ['expediente__id', 'expediente__numero', 'sede']
