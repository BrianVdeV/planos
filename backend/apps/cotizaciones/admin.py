from django.contrib import admin
from .models import Cotizacion, Cancelacion


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    """Admin para Cotizaciones"""
    list_display = ['id', 'nombre', 'cliente',
                    'ubicacion', 'fecha', 'user', 'estado']
    list_filter = ['estado', 'user']
    search_fields = ['nombre', 'cliente', 'dni', 'ubicacion']
    readonly_fields = ['fecha']

    fieldsets = (
        ('Información del Cliente', {
            'fields': ('cliente', 'dni', 'ubicacion', 'pisos')
        }),
        ('Detalles de la Cotización', {
            'fields': ('nombre', 'titulo', 'detalles', 'area', 'telefono', 'observaciones', 'tipo')
        }),
        ('Estado y Usuario', {
            'fields': ('estado', 'user', 'fecha', 'elaboracion')
        }),
    )


@admin.register(Cancelacion)
class CancelacionAdmin(admin.ModelAdmin):
    """Admin para Cuotas de Cancelación"""
    list_display = ['id', 'cotizacion', 'descripcion', 'monto', 'fecha']
    list_filter = ['fecha']
    search_fields = ['descripcion',
                     'cotizacion__nombre', 'cotizacion__cliente']

    def get_queryset(self, request):
        """Mostrar cuotas ordenadas por fecha"""
        qs = super().get_queryset(request)
        return qs.select_related('cotizacion').order_by('fecha')
