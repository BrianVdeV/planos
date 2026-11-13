"""Clases usando DRF"""
from collections import defaultdict
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.utils.timezone import now, timedelta
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend

from apps.calendario.views import CalendarioView
from apps.expedientes.models import Expediente
from gastos.models import ReporteGasto
from kanban.models import Actividad, Tarea

from .models import Access, Ot, TipOt
from .serializers import (
    OtDataSerializer,
    OtSerializer,
    SidebarSerializer,
    TipOtSerializer,
)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class OtViewSet(viewsets.ModelViewSet):
    """Lista todas las ot"""
    queryset = Ot.objects.all()
    serializer_class = OtSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'nombre']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(privado=False)

    @action(detail=False, methods=['get'])
    def histograma_mensual(self, request):
        """Devuelve datasets mensuales y el promedio mensual de OTs creadas."""
        anio_actual = now().year
        try:
            anio_solicitado = int(
                request.query_params.get('year', anio_actual))
        except (ValueError, TypeError):
            anio_solicitado = anio_actual

        labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                  "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        datasets = []

        ots = self.get_queryset().filter(inicio__year=anio_solicitado).order_by('color')
        total_ots_anio = ots.count()

        if anio_solicitado == anio_actual:
            meses_divisor = max(now().month, 1)
        else:
            meses_divisor = 12

        promedio_mensual = round(total_ots_anio / meses_divisor, 1)

        for ot in ots:
            data_mensual = [0] * 12
            if ot.inicio:
                mes_indice = ot.inicio.month - 1
                data_mensual[mes_indice] = 1
                color = ot.color if ot.color else "#727cf5"
                datasets.append({
                    "label": str(ot),
                    "data": data_mensual,
                    "backgroundColor": color,
                    "borderColor": color,
                    "borderWidth": 1
                })

        return Response({
            "labels": labels,
            "datasets": datasets,
            "promedio_mensual": promedio_mensual,
            "total_ots": total_ots_anio
        })

    @action(detail=False, methods=['get'])
    def recientes(self, request):
        ots = self.get_queryset().order_by('-inicio')[:5]
        serializer = self.get_serializer(ots, many=True)
        return Response(serializer.data)


class OTListAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Ot.objects.all()
    serializer_class = OtDataSerializer
    filter_backends = [DatatablesFilterBackend]

    def get_queryset(self):
        expedientes_qs = Expediente.objects.order_by('-id')
        return Ot.objects.annotate(
            total_t=Count('tarea'),
            c_todo=Count('tarea', filter=Q(tarea__estado='todo')),
            c_progress=Count('tarea', filter=Q(tarea__estado='in_progress')),
            c_review=Count('tarea', filter=Q(tarea__estado='review')),
            c_done=Count('tarea', filter=Q(tarea__estado='done')),
        ).prefetch_related(
            Prefetch(
                'expediente_set',
                queryset=expedientes_qs,
                to_attr='lista_expedientes'  # Atributo temporal en memoria
            )
        ).order_by('-id')

    def list(self, request, *args, **kwargs):
        """Modifica la respuesta para que sea compatible con DataTables"""
        draw = int(request.GET.get("draw", 1))
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 50))
        search_value = request.GET.get("search[value]", "").strip()

        queryset = self.filter_queryset(self.get_queryset())
        estado = request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)
        if search_value:
            queryset = queryset.filter(
                Q(nombre__icontains=search_value) |
                Q(id__icontains=search_value) |
                Q(expediente__estado__icontains=search_value)
            )

        total_count = queryset.count()
        paginator = Paginator(queryset, length)
        page_number = (start // length) + 1
        page = paginator.get_page(page_number)
        serializer = self.get_serializer(page, many=True)

        return Response({
            "draw": draw,
            "recordsTotal": total_count,
            "recordsFiltered": total_count,
            "data": serializer.data,
        })


class ChartView(APIView):
    """Grafico ot y colaboradores agrupados por dia"""

    def get(self, request, *args, **kwargs):
        search = request.GET.get('search[value]', '').strip()
        start_date = request.GET.get('start_date', '2025-03-02')
        end_date = request.GET.get('end_date', '2025-03-08')

        try:
            start_range = datetime.strptime(start_date, "%Y-%m-%d")
            end_range = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return Response({"error": "Formato de fecha inválido"}, status=400)

        date_range = [(start_range + timedelta(days=i)).strftime("%Y-%m-%d")
                      for i in range((end_range - start_range).days + 1)]

        queryset = Actividad.objects.filter(
            fin__isnull=False,
            inicio__date__range=(start_date, end_date)
        )

        if search:
            if search.isdigit():
                queryset = queryset.filter(ot_id=search)
            else:
                try:
                    queryset = queryset.filter(
                        user__username__icontains=search)
                except Exception as e:
                    return Response({"error": f"Error al buscar usuario: {str(e)}"}, status=500)

        queryset = queryset.order_by('-ot')
        data = defaultdict(lambda: {date: 0 for date in date_range})
        data_label = defaultdict(lambda: {date: "0:00" for date in date_range})
        totals = {date: 0 for date in date_range}
        totals_label = {date: "0:00" for date in date_range}

        for actividad in queryset:
            fecha = actividad.fin.strftime("%Y-%m-%d")
            ot_label = str(actividad.ot)[
                :20] if actividad.ot else "Sin OT"
            color = actividad.ot.color if actividad.ot else "#000000"
            total_minutos = int(actividad.total_decimal() * 60)
            data[ot_label][fecha] += total_minutos
            totals[fecha] += total_minutos
            if "color" not in data[ot_label]:
                data[ot_label]["color"] = color

        for ot_label, fechas in data.items():
            for fecha in fechas:
                if fecha != "color":
                    minutos = fechas[fecha]
                    horas = minutos // 60
                    restante = minutos % 60
                    data_label[ot_label][fecha] = f"{horas}:{str(restante).zfill(2)}"

        for fecha in totals:
            minutos = totals[fecha]
            horas = minutos // 60
            restante = minutos % 60
            totals_label[fecha] = f"{horas}:{str(restante).zfill(2)}"

        datasets = [
            {
                "label": ot_label,
                "data": [data[ot_label][fecha] / 60 for fecha in date_range],
                "data_label": [data_label[ot_label][fecha] for fecha in date_range],
                "backgroundColor": data[ot_label]["color"]
            }
            for ot_label in data
        ]

        return Response({
            "labels": date_range,
            "datasets": datasets,
            "totals": [totals_label[fecha] for fecha in date_range]
        })


class JqueryToastView(APIView):
    """Notificaciones para el frontend usando jQuery Toast"""

    def get(self, request, *args, **kwargs):
        """GET"""
        if not request.user.is_superuser:
            return Response([], status=200)

        reportes = ReporteGasto.objects.filter(estado_aprobacion=1)
        data = [{
            "titulo": "Aprobaciones pendientes",
            "descripcion":  f"La diferencia es de: {reporte.vuelto}",
            "tipo": "reporte",
        } for reporte in reportes]

        return Response(data)


class TipOtViewSet(viewsets.ModelViewSet):
    """Tipo OT"""
    queryset = TipOt.objects.all().order_by('id')
    serializer_class = TipOtSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [AllowAny]


class NotificacionesView(APIView):
    """API para notificaciones en los próximos 7 días"""

    def get(self, request):
        hoy = datetime.now().date()
        fin = hoy + timedelta(days=7)

        # Obtener eventos desde el CalendarioView
        base_view = CalendarioView()
        response = base_view.get(request)
        eventos = response.data

        proximos = []
        for evento in eventos:
            start_str = evento.get('start')
            end_str = evento.get('end')
            className = evento.get('className', '')

            # Intentar parsear start
            try:
                start_dt = datetime.fromisoformat(start_str)
            except Exception:
                continue

            # Filtrar rango de fechas (solo día)
            if not (hoy <= start_dt.date() <= fin):
                continue

            # Filtrar eventos bg-primary que ya pasaron (hora actual > end)
            if className == "bg-primary" and end_str:
                try:
                    end_dt = datetime.fromisoformat(end_str)
                    if now() > end_dt:
                        continue  # ya terminó el evento, no mostrar
                except Exception:
                    pass  # si no puede convertir, lo dejamos pasar por ahora

            # Personalizar contenido
            if className == "bg-primary":
                hora = start_dt.strftime("%H:%M")
                titulo = evento.get('title', 'Nuevo Evento')
                mensaje = f"{hora} {titulo} asignado a {evento.get('usuario', '')}"
            elif className == "bg-info":
                titulo = f"¡Feliz Cumpleaños {evento.get('usuario', '')}!"
                mensaje = f"Se acerca el cumpleaños de {evento.get('usuario', '')}. ¡Te deseamos un feliz cumpleaños!"
            elif className == "bg-warning":
                titulo = evento.get('title', 'Expediente de SUNARP')
                mensaje = "Expediente de SUNARP por max. reingreso."
            elif className == "bg-danger":
                titulo = evento.get('title')
                mensaje = "Expediente de SUNARP próximo a vencer."
            elif className == "bg-success":
                titulo = f"🌴 ¡Vacaciones de  {evento.get('usuario', '')}!"
                start_fmt = datetime.fromisoformat(
                    start_str).strftime("%d/%m")
                end_fmt = datetime.fromisoformat(
                    end_str).strftime("%d/%m")
                mensaje = f"Vacaciones de {evento.get('usuario', '')} del {start_fmt} al {end_fmt}."
            elif className == "bg-dark":
                titulo = evento.get('title', 'Recordatorio')
                mensaje = "Tienes un recordatorio pendiente."
            else:
                titulo = evento.get('title', 'Nuevo Evento')
                mensaje = "Tienes un nuevo evento."

            evento["titulo"] = titulo
            evento["mensaje"] = mensaje

            proximos.append(evento)

        # Ordenar por fecha de inicio
        proximos.sort(key=lambda x: x['start'])

        return Response(proximos)


class SidebarView(APIView):
    """Vista badges sidebar"""
    serializer_class = SidebarSerializer

    def get(self, request, format=None):
        user = request.user

        # 1. LÓGICA DE AGENDA (Tareas nuevas)
        access = Access.objects.filter(
            user=user).order_by("-timestamp").first()
        if user.is_superuser:
            agenda_count = Tarea.objects.filter(
                editado__gt=access.timestamp).count() if access else 0
        elif access:
            agenda_count = Tarea.objects.filter(
                editado__gt=access.timestamp, responsables=user).count()
        else:
            agenda_count = 0

        # 2. LÓGICA DE GASTOS PENDIENTES (Para aprobadores)
        pending_count = ReporteGasto.objects.filter(
            estado_aprobacion=1).count()

        # 3. LÓGICA DE GASTOS RECHAZADOS (Para el usuario actual)
        rejected_count = ReporteGasto.objects.filter(
            estado_aprobacion=0,
            usuario=user
        ).exclude(Q(mensaje__isnull=True) | Q(mensaje__exact='')).count()

        return Response({
            "agenda": agenda_count,
            "pending": pending_count,
            "rejected": rejected_count
        })
