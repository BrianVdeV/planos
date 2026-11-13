from django.contrib import admin
from .models import Area, Colaborador
# Register your models here.


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    """Admin para Colaboradores"""
    list_display = ['id', 'user','dni','nacimiento']

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """Admin para Áreas"""
    list_display = ['id', 'nombre']