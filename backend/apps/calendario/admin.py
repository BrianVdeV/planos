from django.contrib import admin
from .models import Evento, Recordatorio


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'inicio', 'ot']


@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ['id', 'evento', 'cantidad', 'unidad']
