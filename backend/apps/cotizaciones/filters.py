import django_filters
from django.db.models import Q
from .models import Cotizacion


class CotizacionFilterSet(django_filters.FilterSet):
    """FilterSet personalizado para Cotizacion con búsqueda avanzada"""

    # Búsqueda global
    search = django_filters.CharFilter(
        method='filter_search',
        label='Búsqueda global'
    )

    # Filtros por rango de fechas
    fecha_inicio = django_filters.DateFilter(
        field_name='fecha',
        lookup_expr='gte',
        label='Fecha inicio (>=)'
    )
    fecha_fin = django_filters.DateFilter(
        field_name='fecha',
        lookup_expr='lte',
        label='Fecha fin (<=)'
    )

    # Filtros simples por columna
    nombre = django_filters.CharFilter(
        field_name='nombre',
        lookup_expr='icontains'
    )
    estado = django_filters.ChoiceFilter(
        choices=Cotizacion.ESTADO,
        label='Estado'
    )
    ubicacion = django_filters.CharFilter(
        field_name='ubicacion',
        lookup_expr='icontains',
        label='Ubicacion'
    )
    cliente = django_filters.CharFilter(
        field_name='cliente',
        lookup_expr='icontains',
        label='Cliente (contiene)'
    )
    usuario = django_filters.CharFilter(
        field_name='user__id',
        lookup_expr='exact',
        label='Cotizador'
    )

    class Meta:
        model = Cotizacion
        fields = ['estado', 'cliente', 'nombre', 'ubicacion',
                  'usuario', 'fecha_inicio', 'fecha_fin']

    def filter_search(self, queryset, _name, value):
        """Búsqueda global en múltiples campos"""
        if not value:
            return queryset
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(cliente__icontains=value) |
            Q(ubicacion__icontains=value) |
            Q(id__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(telefono__icontains=value)
        ).distinct()
