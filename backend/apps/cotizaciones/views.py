"""Vista de cotizaciones"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_excel.mixins import XLSXFileMixin
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend

from intranet.models import TipOt

from .filters import CotizacionFilterSet
from .models import Cotizacion
from .serializers import CotizacionCreateSerializer, CotizacionSerializer


@login_required
def cotizaciones_page_view(request):
    usuarios = User.objects.filter(is_active=True)
    tipos_proyecto = TipOt.objects.all()
    context = {
        'tipos_proyecto': tipos_proyecto,
        'usuarios': usuarios
    }
    return render(request, 'cotizaciones.html', context)


class CotizacionViewSet(XLSXFileMixin, viewsets.ModelViewSet):
    """View"""
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter,
                       OrderingFilter, DatatablesFilterBackend]
    filterset_class = CotizacionFilterSet
    ordering_fields = ['id', 'nombre', 'cliente', 'ubicacion',
                       'fecha', 'estado', 'user__first_name']
    xlsx_filename = 'cotizaciones.xlsx'
    body = {
        'height': 15,
    }

    def paginate_queryset(self, queryset):
        """Desactiva la paginación cuando es xlsx."""
        if self.request.query_params.get('format') == 'xlsx':
            return None
        return super().paginate_queryset(queryset)

    def create(self, request):
        data = request.data
        formatted_data = {
            "nombre": data.get('nombre'),
            "tipo_id": data.get('tipo'),
            "elaboracion": data.get('elaboracion'),
            "estado": data.get('estado', 'pendiente'),
            "area": data.get('area').replace(' m2', '') if data.get('area') else '',
            "titulo": data.get('titulo'),
            "detalles": data.get('titulo'),
            "cliente": data.get('cliente'),
            "pisos": data.get('pisos'),
            "ubicacion": data.get('ubicacion'),
            "telefono": data.get('telefono'),
            "dni": data.get('dni'),
            "observaciones": data.get('observaciones'),
            "usuario_nombre": data.get('usuario'),
            "cuotas": data.get('cuotas')
        }
        serializer = CotizacionCreateSerializer(data=formatted_data)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    cotizacion = serializer.save()
                    return Response({"success": True, "message": "Guardado exitoso", "id": cotizacion.id}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
