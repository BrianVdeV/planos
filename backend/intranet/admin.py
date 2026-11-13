"""Vista de admin"""
from django.contrib import admin
from .models import Etiqueta, Ot, TipOt


@admin.register(Ot)
class OtAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'estado')
    search_fields = ('id', 'nombre', 'estado')
    list_filter = ('estado',)


@admin.register(TipOt)
class TipOtAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nom_tipo', 'tipo')
    search_fields = ('codigo', 'nom_tipo', 'tipo')
    list_filter = ('tipo',)


admin.site.register(Etiqueta)
