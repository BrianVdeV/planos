"""Vista API"""
from collections import defaultdict
from decimal import Decimal

import django_filters
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q, Count, Sum
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from drf_excel.mixins import XLSXFileMixin
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend

from gastos.models import CajaChica, Contrato, Gasto, ReporteGasto, Saldo
from gastos.serializers import (
    CajaChicaSerializer,
    ContratoSerializer,
    GastoSerializer,
    ReporteGastoSerializer,
    SaldoSerializer,
)


class GastoFilter(django_filters.FilterSet):
    fecha_inicio = django_filters.DateFilter(
        field_name='reporte__fecha', lookup_expr='gte')
    fecha_fin = django_filters.DateFilter(
        field_name='reporte__fecha', lookup_expr='lte')

    class Meta:
        model = Gasto
        fields = ['reporte', 'reporte__usuario', 'categoria', 'ot']


class GastoViewSet(XLSXFileMixin, viewsets.ModelViewSet):
    """Vista para Gasto"""
    queryset = Gasto.objects.all().order_by('-id')
    serializer_class = GastoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter,
                       OrderingFilter, DatatablesFilterBackend]
    filterset_class = GastoFilter
    search_fields = ['descripcion', 'ot__id', 'ot__nombre']
    filename = 'gastos.xlsx'
    body = {
        'height': 15,
    }

    def paginate_queryset(self, queryset):
        """Desactiva la paginación cuando es xlsx."""
        if self.request.query_params.get('format') == 'xlsx':
            return None
        return super().paginate_queryset(queryset)

    def list(self, request, *args, **kwargs):
        # 1. Obtenemos el queryset con todos los filtros aplicados (fechas, categorias, etc)
        queryset = self.filter_queryset(self.get_queryset())

        # 2. Calculamos la suma total de ese queryset exacto
        total_monto = queryset.aggregate(suma=Sum('monto'))['suma'] or 0

        # 3. Generamos la respuesta normal paginada de DRF
        response = super().list(request, *args, **kwargs)

        # 4. Inyectamos nuestro total en la respuesta JSON para DataTables
        if request.query_params.get('format') == 'datatables':
            if isinstance(response.data, dict):
                response.data['total_monto_filtrado'] = total_monto

        return response

    @action(detail=False, methods=['get'])
    def gastos_por_fecha(self, request):
        """ApexCharts"""
        fecha_inicio = request.GET.get('fechaInicio')
        fecha_fin = request.GET.get('fechaFin')
        queryset = Gasto.objects.all()
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(reporte__fecha__range=[
                                       fecha_inicio, fecha_fin])
        gastos_agrupados = queryset.values('reporte__fecha').annotate(
            total=Sum('monto')).order_by('reporte__fecha')
        fechas = [gasto['reporte__fecha'].strftime(
            '%d %b') for gasto in gastos_agrupados]
        totales = [round(gasto['total'], 2) for gasto in gastos_agrupados]
        return Response({
            "labels": fechas,
            "data": totales
        })

    @action(detail=False, methods=['get'])
    def gastos_por_categoria(self, request):
        """ApexCharts Dona"""
        fecha_inicio = request.GET.get('fechaInicio')
        fecha_fin = request.GET.get('fechaFin')

        fecha_inicio = parse_date(fecha_inicio) if fecha_inicio else None
        fecha_fin = parse_date(fecha_fin) if fecha_fin else None
        gastos = Gasto.objects.all()
        if fecha_inicio and fecha_fin:
            gastos = gastos.filter(reporte__fecha__range=[
                                   fecha_inicio, fecha_fin])
        gastos_agrupados = gastos.values('categoria').annotate(
            total=Sum('monto'), cantidad=Count('id')).order_by('-total')
        labels = [gasto['categoria'] for gasto in gastos_agrupados]
        data = [round(gasto['total'], 2) for gasto in gastos_agrupados]
        cantidad = [gasto['cantidad'] for gasto in gastos_agrupados]
        return Response({
            "labels": labels,
            "data": data,
            "cantidad": cantidad
        })


class ReporteGastoViewSet(viewsets.ModelViewSet):
    """Vista para Reporte de Gastos"""
    queryset = ReporteGasto.objects.all().order_by('-id')
    serializer_class = ReporteGastoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['usuario', 'estado_aprobacion']

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtiene los reportes pendientes de aprobación"""
        queryset = self.get_queryset().filter(estado_aprobacion=1)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def rechazados(self, request):
        """Obtiene los reportes rechazados"""
        queryset = self.get_queryset().filter(estado_aprobacion=3)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='mis-reportes')
    def mis_reportes(self, request):
        """Obtiene todos los reportes del usuario autenticado"""
        queryset = self.get_queryset().filter(usuario=request.user)

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='mis-reportes-sin-enviar')
    def mis_reportes_sin_enviar(self, request):
        """Obtiene los reportes del usuario autenticado con estado 0 (Sin Enviar)"""
        queryset = self.get_queryset().filter(
            Q(usuario=request.user) &
            (Q(estado_aprobacion=0) | Q(estado_aprobacion=3))
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='enviar-todos')
    def enviar_todos(self, request):
        """Cambia todos los reportes 'Sin Enviar' y Rechazados a 'Pendiente' (1)"""
        updated_count = self.get_queryset().filter(
            Q(usuario=request.user) &
            (Q(estado_aprobacion=0) | Q(estado_aprobacion=3))
        ).update(estado_aprobacion=1)

        if updated_count > 0:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admin_notifications",  # 👈 Apuntamos solo a los administradores
                {
                    "type": "send.notification",  # Llama al método del Consumer
                    "data": {
                        "tipo": "nuevo_reporte_admin",
                        "titulo": "Nuevos Reportes Pendientes",
                        "cuerpo": f"{request.user.username} ha enviado {updated_count} gastos para aprobación.",
                        "usuario_id": request.user.id
                    }
                }
            )

        return Response({"success": True, "actualizados": updated_count})

    @action(detail=True, methods=['post'], url_path='rechazar')
    def rechazar_reporte(self, request, pk=None):
        """Rechaza un reporte, guarda el motivo y notifica al usuario"""
        # Obtenemos el reporte específico
        reporte = self.get_object()
        mensaje_rechazo = request.data.get('mensaje', '')

        # Actualizamos la base de datos
        reporte.estado_aprobacion = 3
        reporte.mensaje = mensaje_rechazo
        reporte.save()

        # Enviamos la notificación por WebSocket SOLO al dueño de este reporte
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            # 👈 El grupo privado del usuario
            f"user_notifications_{reporte.usuario.id}",
            {
                "type": "send.notification",
                "data": {
                    "tipo": "reporte_rechazado",
                    "titulo": "Reporte Rechazado",
                    "cuerpo": f"Tu reporte del {reporte.fecha} ha sido rechazado. Motivo: {mensaje_rechazo}",
                    "reporte_id": reporte.id
                }
            }
        )

        return Response({"success": True, "mensaje": "Reporte rechazado correctamente."})


class CajaChicaAgrupadaView(APIView):
    """Vista de la caja chica igualito al excel que quiere Betci >:c"""

    def partial_update(self, request, pk=None):

        instance = self.get_object()
        ingreso = request.data.get('ingreso')
        if ingreso:
            instance.ingreso = ingreso
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Convierte a fechas
        if start_date and end_date:
            try:
                start_date = parse_date(start_date)
                end_date = parse_date(end_date)
            except ValueError:
                start_date = end_date = None
        else:
            start_date = end_date = None

        if start_date and end_date:
            caja_list = CajaChica.objects.filter(
                fecha__range=(start_date, end_date)
            ).order_by('fecha')
        else:
            caja_list = CajaChica.objects.order_by('fecha')

        # ← solo convierte a lista lo que ya filtraste
        caja_list = list(caja_list)

        # Filtra reportes
        reportes = ReporteGasto.objects.filter(
            estado_aprobacion=2).order_by('fecha', 'id')
        if start_date and end_date:
            reportes = reportes.filter(fecha__range=(start_date, end_date))

        reportes_por_fecha = defaultdict(list)
        for reporte in reportes:
            reportes_por_fecha[reporte.fecha].append(reporte)

        result = []

        for i, caja in enumerate(caja_list):
            fecha_inicio = caja.fecha
            fecha_fin = caja_list[i + 1].fecha if i + \
                1 < len(caja_list) else None

            saldo_actual = Decimal(caja.saldo_inicial) + Decimal(caja.ingreso)
            total_gastos = Decimal(0)
            reportes_data = []

            for reporte in reportes:
                if reporte.fecha >= fecha_inicio and (not fecha_fin or reporte.fecha < fecha_fin):
                    total_gastos += reporte.total
                    saldo_actual -= reporte.total
                    data = ReporteGastoSerializer(reporte).data
                    data['saldo'] = str(saldo_actual.quantize(Decimal('0.01')))
                    reportes_data.append(data)

            result.append({
                'id_cajachica': caja.id,
                'fecha_ingreso': caja.fecha,
                'ingreso': str(Decimal(caja.ingreso).quantize(Decimal('0.01'))),
                'total1': str(Decimal(caja.saldo_actual).quantize(Decimal('0.01'))),
                'totales': str(Decimal(total_gastos).quantize(Decimal('0.01'))),
                'saldo1': str(Decimal(caja.saldo_inicial).quantize(Decimal('0.01'))),
                'saldo2': str(Decimal(saldo_actual).quantize(Decimal('0.01'))),
                'reportes': reportes_data
            })
        return Response(result)


class ActualizarIngresoView(APIView):

    def patch(self, request, id):
        # Primero verificamos si el usuario está autenticado
        if not request.user.is_authenticated:
            return Response({"detail": "No estás autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Obtener el objeto CajaChica por su ID
            caja = CajaChica.objects.get(id=id)
        except CajaChica.DoesNotExist:
            return Response({"detail": "Objeto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Obtener el valor del 'ingreso' desde la solicitud
        ingreso = request.data.get('ingreso')

        if ingreso is not None:
            try:
                # Asegurarse de que el 'ingreso' es un valor decimal
                ingreso_decimal = Decimal(ingreso)
                caja.ingreso = ingreso_decimal
                caja.save()

                # Serializa el objeto actualizado
                serializer = CajaChicaSerializer(caja)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": f"Error al guardar los datos: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"detail": "El campo 'ingreso' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)


class SaldoViewSet(viewsets.ModelViewSet):
    """Vista para saldo"""
    queryset = Saldo.objects.all().order_by('id')
    serializer_class = SaldoSerializer


class ContratoViewSet(viewsets.ModelViewSet):
    """Vista para contrato"""
    queryset = Contrato.objects.all().order_by('id')
    serializer_class = ContratoSerializer
