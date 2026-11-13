"""Vista de Expediente"""
from datetime import datetime

import django_filters
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_excel.mixins import XLSXFileMixin
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend

from .forms import ExpedienteForm
from .models import Expediente, ExpedienteActo, ExpedientePago
from .serializers import ExpedientePagoSerializer, ExpedienteSerializer


def guardar_datos_sunarp(expediente, datos_sunarp):
    """
    Recibe la instancia del Expediente y el JSON desencriptado.
    Actualiza el maestro y crea los detalles.
    """
    lst_titulo = datos_sunarp.get('lstTitulo', [])
    lst_pagos = datos_sunarp.get('lstPagos', [])
    estado_devo_data = datos_sunarp.get('estadoDevo', {})

    if not lst_titulo:
        return False, "El JSON no contiene actos registrales (lstTitulo vacío)."

    # 🌟 Usamos una transacción atómica por seguridad de la base de datos
    try:
        with transaction.atomic():

            # ==========================================
            # 1. ACTUALIZAR EL MAESTRO (Expediente)
            # ==========================================
            # Tomamos el primer acto de la lista como referencia para los datos generales
            acto_referencia = lst_titulo[0]
            estado_actual = acto_referencia.get('estadoActual', '')
            if estado_actual.lower() == 'en calificacion':
                expediente.estado = 'En calificación'
            else:
                expediente.estado = estado_actual.capitalize()
            expediente.presentante = acto_referencia.get('nombrePresentante')

            # Mapeo de Fechas (SUNARP envía 'DD/MM/YYYY' y 'DD/MM/YYYY HH:MM:SS')
            vencimiento_str = acto_referencia.get('fechaVencimiento')
            if vencimiento_str:
                expediente.vencimiento = datetime.strptime(
                    vencimiento_str, '%d/%m/%Y').date()

            presentacion_str = acto_referencia.get('fechaHoraPresentacion')
            if presentacion_str:
                # Extraemos solo la fecha para el campo DateField
                expediente.presentacion = datetime.strptime(
                    presentacion_str, '%d/%m/%Y %H:%M:%S').date()

            if estado_devo_data:
                expediente.estado_devo = estado_devo_data.get('estado')
                monto_str = estado_devo_data.get('montoDevo')
                if monto_str:
                    try:
                        expediente.monto_devo = float(monto_str)
                    except (ValueError, TypeError):
                        expediente.monto_devo = None
            expediente.save()

            # ==========================================
            # 2. GUARDAR LOS ACTOS (ExpedienteActo)
            # ==========================================
            for acto in lst_titulo:
                # get_or_create evita duplicados si corres el scraper 2 veces sobre el mismo expediente
                ExpedienteActo.objects.get_or_create(
                    expediente=expediente,
                    partida_matriz=acto.get('partidaMatriz'),
                    cod_acto=acto.get('codActo'),
                    defaults={
                        'acto_registral': acto.get('actoRegistral')
                    }
                )

            # ==========================================
            # 3. GUARDAR LOS PAGOS (ExpedientePago)
            # ==========================================
            for pago in lst_pagos:
                monto_str = pago.get('montoRecibo', '0')
                fecha_recibo_str = pago.get('fechaRecibo')

                # Convertir el string del monto quitando los espacios en blanco
                monto_limpio = float(
                    monto_str.strip()) if monto_str.strip() else 0.00

                # Convertir fecha y hora (este modelo sí es DateTimeField)
                fecha_obj = None
                if fecha_recibo_str:
                    fecha_obj = datetime.strptime(
                        fecha_recibo_str, '%d/%m/%Y %H:%M:%S')

                ExpedientePago.objects.get_or_create(
                    expediente=expediente,
                    numero_recibo=pago.get('numeroRecibo'),
                    defaults={
                        'monto': monto_limpio,
                        'fecha': fecha_obj,
                        'sede': pago.get('desSedePago')
                    }
                )

        return True, "Datos guardados correctamente."

    except Exception as e:
        return False, f"Error de base de datos al guardar: {str(e)}"


@login_required
def expedientes(request):
    """ Renderiza la plantilla HTML principal (Solo Sunarp) """
    estados = Expediente.ESTADOS
    form = ExpedienteForm()
    context = {
        'estados': estados,
        'form': form,
    }
    return render(request, 'expedientes.html', context)


class ExpedienteViewSet(viewsets.ModelViewSet):
    """ViewSet"""
    queryset = Expediente.objects.all().order_by('-ot')
    serializer_class = ExpedienteSerializer


class ExpedienteFilter(django_filters.FilterSet):
    class Meta:
        model = Expediente
        fields = ['ot', 'estado', 'oficina', 'entidad', 'ot__estado']


class SunarpViewSet(XLSXFileMixin, viewsets.ModelViewSet):
    """ViewSet específico para expedientes de SUNARP"""
    queryset = Expediente.objects.filter(
        entidad='Sunarp').select_related('ot').order_by('-ot')
    serializer_class = ExpedienteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter,
                       OrderingFilter, DatatablesFilterBackend]
    filterset_class = ExpedienteFilter
    search_fields = ['numero', 'presentante', 'ot__nombre']
    ordering_fields = ['ot__id', 'presentacion', 'vencimiento']
    filename = 'sunarp.xlsx'
    body = {
        'height': 15,
    }

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        pagos = instance.pagos.all()
        data['pagos'] = ExpedientePagoSerializer(pagos, many=True).data
        partidas_unicas = instance.actos.values_list(
            'partida_matriz', flat=True).distinct()
        actos_unicos = instance.actos.values(
            'cod_acto', 'acto_registral').distinct()
        data['actos'] = list(actos_unicos)
        data['partidas'] = list(partidas_unicas)
        return Response(data)

    def paginate_queryset(self, queryset):
        """Desactiva la paginación cuando es xlsx."""
        if self.request.query_params.get('format') == 'xlsx':
            return None
        return super().paginate_queryset(queryset)

    @action(detail=False, methods=['get'], url_path='pendientes')
    def obtener_pendientes(self, request):
        """API COMPLETA: Filtra expedientes Sunarp"""
        queryset = Expediente.objects.filter(entidad='Sunarp', ot__estado='Activo').exclude(
            Q(estado__in=['Inscrito', 'Tachado', 'Finalizado',
                          'Entregado al Cliente']) |
            Q(numero__in=['0', '', None]) |
            Q(ot__nombre__startswith='BUS')
        ).select_related('ot').annotate(
            prioridad_estado=Case(
                When(estado='En calificación', then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by('prioridad_estado', 'vencimiento')
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='update-sunarp')
    def update_sunarp(self, request, pk=None):
        expediente = self.get_object()
        datos_sunarp = request.data

        # 2. Guardar en los modelos usando la función que creamos arriba
        exito, mensaje = guardar_datos_sunarp(expediente, datos_sunarp)

        if exito:
            return Response({"mensaje": mensaje}, status=status.HTTP_200_OK)
        else:
            return Response({"error": mensaje}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ====================================================================
#  ZONA DE MUNICIPALIDAD Y OTROS (TU NUEVO MÓDULO)
# ====================================================================


@login_required
def municipalidad_otros_view(request):
    """ Renderiza la plantilla HTML de Muni/Otros """
    form = ExpedienteForm()
    context = {
        'estados': Expediente.ESTADOS,
        'form': form,
    }
    return render(request, 'municipalidad_otros.html', context)


class MunicipalidadViewSet(viewsets.ModelViewSet):
    """ViewSet específico para Municipalidad y Otros (TODO MENOS SUNARP)"""
    queryset = Expediente.objects.exclude(
        entidad='Sunarp').select_related('ot').order_by('-creado')
    serializer_class = ExpedienteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter,
                       OrderingFilter, DatatablesFilterBackend]
    filterset_class = ExpedienteFilter
    search_fields = ['numero', 'ot__nombre']
    ordering_fields = ['ot__id', 'presentacion', 'vencimiento']
