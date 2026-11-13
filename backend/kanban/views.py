"""Vista de Tareas y Actividad"""
import datetime
from datetime import date, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.timezone import now
from django_filters import CharFilter, FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from auth.models import Colaborador
from intranet.models import Access, Ot

from .forms import TareaForm
from .models import Actividad, Tarea
from .serializers import ActividadSerializer, InformesSerializer, TareaSerializer


@login_required
def tarea_kanban_view(request):
    """Template kanban"""
    form = TareaForm()

    # --- AGREGAR ESTO: ---
    users = User.objects.filter(is_active=True)
    # ---------------------

    access, created = Access.objects.get_or_create(
        user=request.user,
        url=request.path,
    )
    access.timestamp = now()
    access.save()

    context = {
        "form": form,
        "users": users  # <--- IMPORTANTE: AGREGAR ESTO AL CONTEXTO
    }
    return render(request, "kanban.html", context)


@login_required
def tarea_lista_view(request):
    """Vista para mostrar la lista de tareas"""
    form = TareaForm()

    # Obtener todos los usuarios activos para el filtro
    users = User.objects.filter(is_active=True)

    # --- NUEVO: OBTENER ÁREA DEL USUARIO ---
    nombre_area = ""
    try:
        # Buscamos al colaborador conectado
        colaborador = Colaborador.objects.get(user=request.user)
        if colaborador.area:
            nombre_area = colaborador.area.nombre
    except Colaborador.DoesNotExist:
        pass
    except Exception:
        pass
    # ---------------------------------------

    context = {
        "form": form,
        "users": users,       # Para los filtros
        "nombre_area": nombre_area  # <--- ESTA ES LA CLAVE PARA EL IF EN EL HTML
    }
    return render(request, 'tareas.html', context)


class TareaFilter(FilterSet):
    """Definimos un nuevo campo de filtro llamado 'vencimiento_rango'"""
    vencimiento_rango = CharFilter(method='filter_vencimiento_rango')
    area = CharFilter(
        field_name='user__colaborador__area__nombre', lookup_expr='icontains')
    today = date.today()

    class Meta:
        """Meta"""
        model = Tarea
        fields = ['ot', 'responsables', 'vencimiento', 'area']

    def filter_vencimiento_rango(self, queryset, name, value):
        """El 'value' será el texto enviado desde el frontend (ej: 'today', 'past7days')"""
        if value == 'today':
            return queryset.filter(vencimiento=self.today)
        elif value == 'pastweek':
            seven_days_ago = self.today - timedelta(days=7)
            return queryset.filter(vencimiento__date__range=[seven_days_ago, self.today])
        elif value == 'thisweek':
            start_of_week = self.today - timedelta(days=self.today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return queryset.filter(vencimiento__date__range=[start_of_week, end_of_week])
        elif value == 'thismonth':
            return queryset.filter(
                vencimiento__year=self.today.year, vencimiento__month=self.today.month)
        elif value == 'thisyear':
            return queryset.filter(vencimiento__year=self.today.year)
        return queryset


class TareaViewSet(viewsets.ModelViewSet):
    """API Tarea"""
    queryset = Tarea.objects.all().order_by('-vencimiento')
    serializer_class = TareaSerializer
    # Asegura que solo usuarios autenticados accedan
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TareaFilter
    filterset_fields = ['ot', 'responsables']
    ordering_fields = ['titulo']

    @action(detail=False, methods=['get'])
    def datatables(self, request):
        """Modifica la respuesta para que sea compatible con DataTables"""

        draw = int(request.GET.get("draw", 1))
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))
        # El 'search_value' ahora viene de d.search, no de search[value]
        search_value = request.GET.get("search[value]", "").strip()

        # Obtenemos el queryset base
        queryset = self.get_queryset()

        # Total de registros SIN filtrar
        records_total = queryset.count()

        # --- FILTROS ---
        # Obtenemos los parámetros de los filtros personalizados
        estado = request.GET.get('estado')
        responsable_id = request.GET.get('responsable')
        rango_vencimiento = request.GET.get('vencimiento')

        # Filtro de búsqueda general
        if search_value:
            queryset = queryset.filter(
                Q(titulo__icontains=search_value) |
                Q(descripcion__icontains=search_value) |
                Q(ot__id__icontains=search_value) |
                Q(ot__nombre__icontains=search_value)
            )

        if estado:
            queryset = queryset.filter(estado=estado)

        if responsable_id:
            queryset = queryset.filter(responsables=responsable_id)

        if rango_vencimiento and ' to ' in rango_vencimiento:
            try:
                start_date, end_date = rango_vencimiento.split(' to ')
                queryset = queryset.filter(vencimiento__date__range=[
                    start_date, end_date])
            except ValueError:
                pass

        # --- ORDENAMIENTO (SECCIÓN CORREGIDA) ---

        # 1. Intentar obtener el orden de DataTables (clic en flechas)
        order_column_index = request.GET.get('order[0][column]')
        order_dir = request.GET.get('order[0][dir]', 'asc')

        # 2. Obtener el orden del dropdown personalizado
        custom_ordering = request.GET.get('ordering')

        # Mapeo de índice de columna a campo del modelo
        # Debe coincidir con el orden en 'columns' de JavaScript
        column_field_map = [
            'estado',              # 0
            'ot__id',           # 1 (Ordenamos por el ID de la OT)
            'titulo',
            'responsables__username',
            'vencimiento',         # 3
            'duracion',            # 4
            None                   # 6 (Acciones, no ordenable)
        ]

        order_field = None

        if order_column_index is not None:
            try:
                col_index = int(order_column_index)
                field_name = column_field_map[col_index]

                if field_name:
                    prefix = '-' if order_dir == 'desc' else ''
                    order_field = f"{prefix}{field_name}"
            except (IndexError, ValueError):
                pass  # Índice de columna inválido, se ignora

        # 3. Si DataTables no ordenó (no hubo clic en flecha), usar el dropdown
        if not order_field and custom_ordering:
            ordering_map = {
                'titulo_asc': 'titulo',
                'titulo_desc': '-titulo',
                'vencimiento_asc': 'vencimiento',
                'vencimiento_desc': '-vencimiento',
                'duracion_asc': 'duracion',
                'duracion_desc': '-duracion',
            }
            order_field = ordering_map.get(custom_ordering)

        # 4. Aplicar el ordenamiento
        if order_field:
            queryset = queryset.order_by(order_field)
        else:
            # Orden por defecto si no se especifica (más nuevos primero)
            queryset = queryset.order_by('-id')
        # --- FIN DE SECCIÓN CORREGIDA ---

        # Total de registros DESPUÉS de aplicar los filtros
        records_filtered = queryset.count()

        # --- PAGINACIÓN ---
        # Paginación sobre el queryset ya filtrado y ordenado
        paginated_queryset = queryset[start: start + length]

        serializer = self.get_serializer(paginated_queryset, many=True)

        return Response({
            "draw": draw,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered,  # Corregido
            "data": serializer.data,
        })

    @action(detail=True, methods=['post'], url_path='iniciar')
    def iniciar(self, request, pk=None):
        """Inicia una actividad basada en esta Tarea."""
        try:
            tarea = self.get_object()
            user = request.user
            actividad_actual = Actividad.objects.filter(
                user=user, fin=None).first()

            if actividad_actual:
                actividad_actual.fin = timezone.now()
                actividad_actual.save()
            comentario_inicial = tarea.titulo

            if tarea.descripcion:
                comentario_inicial = f"{tarea.descripcion}"

            if len(comentario_inicial) < 25:
                comentario_inicial = comentario_inicial.ljust(25, '.')

            comentario_inicial = comentario_inicial[:500]

            nueva_actividad = Actividad.objects.create(
                user=user,
                ot=tarea.ot,
                tarea=tarea,
                inicio=timezone.now(),
                fin=None,
                comentario=comentario_inicial
            )

            tarea.estado = 'in_progress'
            tarea.save()

            serializer = ActividadSerializer(nueva_actividad)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class KanbanViewSet(viewsets.ReadOnlyModelViewSet):
    """API Tarea"""
    queryset = Tarea.objects.all().prefetch_related(
        'responsables__colaborador'
    ).order_by('-id')
    serializer_class = TareaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TareaFilter
    filterset_fields = ['ot', 'user']
    ordering_fields = ['titulo']

    @action(detail=False, methods=['get'], url_path='mi-kanban')
    def mi_kanban(self, request):
        """Devuelve las tareas del usuario autenticado en formato Kanban."""
        hoy = date.today()
        queryset = self.get_queryset().filter(responsables=request.user)

        queryset = self.get_queryset().filter(
            Q(responsables__in=[request.user])
        ).distinct()

        tareas = []
        for tarea in queryset:
            if tarea.estado == 'done':
                if tarea.editado.date() == hoy:
                    tareas.append(tarea)
            else:
                tareas.append(tarea)

        serializer = self.get_serializer(tareas, many=True)
        return Response(serializer.data)


@login_required
def add_tarea(request):
    """Vista para agregar una nueva tarea"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        ot_id = request.POST.get('ot')
        fecha_vencimiento = request.POST.get('vencimiento')  # YYYY-MM-DD
        responsables_ids = request.POST.getlist('responsables')

        ot_instance = None
        duracion = None  # Inicializar duracion

        if ot_id:
            ot_instance = Ot.objects.filter(id=ot_id).first()

        vencimiento = None
        if fecha_vencimiento:
            try:
                # --- AQUÍ ESTÁ LA CORRECCIÓN DEL PRIMER ERROR ---
                vencimiento = datetime.datetime.strptime(
                    fecha_vencimiento, "%Y-%m-%d")
            except ValueError:
                vencimiento = None  # Asignar None si el formato es incorrecto

        tarea = Tarea.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            ot=ot_instance,
            vencimiento=vencimiento,
            duracion=duracion
        )
        print(responsables_ids)
        if responsables_ids:
            usuarios = User.objects.filter(id__in=responsables_ids)
            tarea.responsables.set(usuarios)
        return redirect('tarea_lista')

    return JsonResponse({'error': 'Método no permitido'}, status=405)


class ActividadViewSet(viewsets.ModelViewSet):
    """ViewSet para las actividades"""
    queryset = Actividad.objects.all().order_by('-id')
    serializer_class = ActividadSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ot', 'tarea', 'user']

    def perform_create(self, serializer):
        """Si se envía duración, actualizar la Tarea maestra siempre"""
        with transaction.atomic():
            actividad = serializer.save()
            duracion_input = self.request.data.get('duracion_input')

            if duracion_input:
                try:
                    minutos = int(duracion_input)
                    if minutos > 0:
                        tarea = actividad.tarea
                        # Actualizamos la duración de la tarea maestra
                        tarea.duracion = timedelta(minutes=minutos)
                        tarea.save()
                        print(
                            f"🔄 Tarea '{tarea.titulo}' actualizada a {minutos} minutos.")
                except ValueError:
                    print("⚠️ Error: 'duracion_input' debe ser un número entero.")
                except Exception as e:
                    print(f"❌ Error actualizando duración de tarea: {e}")

    @action(detail=True, methods=['post'])
    def reanudar(self, request, pk=None):
        """Reanuda una actividad"""
        original = self.get_object()
        user = request.user
        actividad = Actividad.objects.filter(
            user=user, fin=None).first()
        if actividad:
            actividad.fin = timezone.now()
            actividad.save()
        nueva_actividad = Actividad.objects.create(
            user=user,
            ot=original.ot,
            tarea=original.tarea,
            inicio=now(),
            fin=None,
            comentario=original.comentario
        )

        serializer = self.get_serializer(nueva_actividad)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def admin_finalizar_actividad(self, request, pk=None):
        """Finaliza la actividad definitivamente y notifica al usuario."""
        if not request.user.is_superuser:
            return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)

        actividad = self.get_object()
        if actividad.fin:
            return Response({'error': 'Ya estaba finalizada'}, status=400)

        # 1. Finalizar la actividad (Tu lógica actual)
        actividad.fin = timezone.now()
        actividad.pausado = False  # Nos aseguramos que NO esté pausada
        actividad.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            # 👈 El grupo privado del usuario
            f"user_notifications_{actividad.user.id}",
            {
                "type": "send.notification",
                "data": {
                    "tipo": "activity-stopped",
                    "titulo": "Actividad Pausada",
                    "cuerpo": "Tu actividad ha sido pausada por un administrador."
                }
            }
        )

        return Response(self.get_serializer(actividad).data)

    # 2. PAUSAR
    @action(detail=True, methods=['post'])
    def admin_pausar_actividad(self, request, pk=None):
        """Detiene la actividad pero la marca como PAUSADA."""
        if not request.user.is_superuser:
            return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)

        actividad = self.get_object()
        if actividad.fin:
            return Response({'error': 'Ya estaba finalizada'}, status=400)

        actividad.fin = timezone.now()
        actividad.pausado = True  # <--- LA MARCAMOS COMO PAUSADA
        actividad.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            # 👈 El grupo privado del usuario
            f"user_notifications_{actividad.user.id}",
            {
                "type": "send.notification",
                "data": {
                    "tipo": "activity-stopped",
                    "titulo": "Actividad Pausada",
                    "cuerpo": "Tu actividad ha sido pausada por un administrador."
                }
            }
        )

        return Response(self.get_serializer(actividad).data)

    # 3. REANUDAR (Desde Admin)
    @action(detail=True, methods=['post'])
    def admin_reanudar_actividad(self, request, pk=None):
        """
        Crea una NUEVA actividad para el usuario basada en la pausada y notifica al usuario.
        """
        if not request.user.is_superuser:
            return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)

        actividad_pausada = self.get_object()
        usuario = actividad_pausada.user

        # Verificar si el usuario YA tiene algo activo (no puede tener 2)
        if Actividad.objects.filter(user=usuario, fin__isnull=True).exists():
            return Response({'error': f'El usuario {usuario.username} ya tiene una actividad en curso. Debe terminarla antes.'}, status=400)

        # Clonamos la actividad
        nueva_actividad = Actividad.objects.create(
            user=usuario,
            ot=actividad_pausada.ot,
            tarea=actividad_pausada.tarea,
            comentario=actividad_pausada.comentario,  # Mantiene el comentario
            duracion=actividad_pausada.duracion,      # Mantiene el estimado
            inicio=timezone.now(),
            fin=None
        )

        actividad_pausada.pausado = False
        actividad_pausada.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            # 👈 El grupo privado del usuario
            f"user_notifications_{actividad_pausada.user.id}",
            {
                "type": "send.notification",
                "data": {
                    "tipo": "activity-stopped",
                    "titulo": "Actividad Pausada",
                    "cuerpo": "Tu actividad ha sido pausada por un administrador."
                }
            }
        )

        return Response(self.get_serializer(nueva_actividad).data)


class InformesViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para informes"""
    serializer_class = InformesSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Actividad.objects.all()
        if not user.is_superuser:
            queryset = queryset.filter(ot__privado=0)

        # Mostrar primero actividades que ya tienen fin (finalizadas), luego orden por inicio descendente
        queryset = queryset.annotate(
            fin_orden=Case(
                When(fin__isnull=False, then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            )
        ).order_by('-fin_orden', '-inicio')

        return queryset

    @action(detail=False, methods=['get'])
    def detallado(self, request):
        """DataTables con filtros y ordenamiento personalizado"""

        draw = int(request.GET.get("draw", 1))
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))
        search_value = request.GET.get("search[value]", "").strip()
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        # NUEVO: Obtener el filtro de estado
        estado_filtro = request.GET.get("estado_filtro", "")

        queryset = self.get_queryset()

        # --- 1. APLICAR FILTRO ESPECÍFICO (DROPDOWN) ---
        if estado_filtro == 'activos':
            queryset = queryset.filter(fin__isnull=True)
        elif estado_filtro == 'pausados':
            queryset = queryset.filter(pausado=True)
        # ELIMINADO: elif estado_filtro == 'finalizados': ...

        # --- 2. FILTROS DE BÚSQUEDA Y FECHA (EXISTENTES) ---
        if search_value:
            queryset = queryset.filter(
                Q(comentario__icontains=search_value) |
                Q(ot__id__icontains=search_value) |
                Q(ot__nombre__icontains=search_value) |
                Q(tarea__titulo__icontains=search_value) |
                Q(user__username__icontains=search_value))

        if start_date and end_date:
            queryset = queryset.filter(
                inicio__date__range=[start_date, end_date])

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

    @action(detail=False, methods=['get'])
    def actividades(self, request):
        """DataTables con agrupación para Admin y lista normal para User"""

        # --- 1. Parámetros de DataTables ---
        draw = int(request.GET.get("draw", 1))
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))
        search_value = request.GET.get("search[value]", "").strip()
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        estado_filtro = request.GET.get("estado_filtro", "")

        # Obtenemos el queryset base
        queryset = self.get_queryset()

        # --- 2. FILTROS GENERALES (Fecha y Búsqueda) ---
        if start_date and end_date:
            queryset = queryset.filter(
                inicio__date__range=[start_date, end_date])

        if search_value:
            queryset = queryset.filter(
                Q(comentario__icontains=search_value) |
                Q(ot__id__icontains=search_value) |
                Q(ot__nombre__icontains=search_value) |
                Q(tarea__titulo__icontains=search_value) |
                Q(user__username__icontains=search_value)
            )

        # Aplicar filtro dropdown
        if estado_filtro == 'activos':
            queryset = queryset.filter(fin__isnull=True)
        elif estado_filtro == 'pausados':
            queryset = queryset.filter(pausado=True)

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
