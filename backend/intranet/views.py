"""Muchas Vistas"""
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.expedientes.models import Expediente
from auth.models import Colaborador
from gastos.models import Gasto, crear_cajas_chicas_faltantes
from intranet.models import Ot, TipOt
from kanban.forms import ActividadForm, TareaForm
from kanban.models import Actividad


@login_required
def list_actividades_index(request):
    """Endpoint para cargar actividades en index.html con DataTables."""

    # 1. Parámetros de DataTables
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    # Longitud de página, 50 por defecto en tu JS
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "").strip()

    # 2. Queryset Base: Actividad del usuario actual y finalizadas
    # Modificamos la lógica que era muy lenta en 'index'
    queryset = Actividad.objects.filter(
        user=request.user.id,
        fin__isnull=False
    ).order_by('-id')

    # 3. Aplicar Filtro de Búsqueda
    if search_value:
        queryset = queryset.filter(
            Q(comentario__icontains=search_value) |
            Q(ot__id__icontains=search_value) |
            Q(tarea__titulo__icontains=search_value)
        )

    records_filtered = queryset.count()
    records_total = records_filtered
    queryset = queryset[start:start + length]
    data = []
    for actividad in queryset:
        expediente = Expediente.objects.filter(
            ot=actividad.ot).order_by('-id').first()
        data.append({
            'id': actividad.id,
            'actividad_desc': actividad.tarea.titulo if actividad.tarea else None,
            'comentario': actividad.comentario,
            'expediente_estado': expediente.estado if expediente else None,
            'expediente_numero': expediente.numero if expediente else None,
            'expediente_reingreso': expediente.reingreso.strftime('%Y-%m-%d') if expediente and expediente.reingreso else None,
            'expediente_vencimiento': expediente.vencimiento.strftime('%Y-%m-%d') if expediente and expediente.vencimiento else None,
            'ot': f"{actividad.ot.id} - {actividad.ot.nombre}" if actividad.ot else None,
            'inicio': actividad.inicio.strftime('%H:%M') if actividad.inicio else None,
            'fin': actividad.fin.strftime('%H:%M') if actividad.fin else None,
            'fecha': actividad.inicio.strftime('%Y-%m-%d') if actividad.inicio else None,
            'total': actividad.total(),
        })
    return JsonResponse({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data,
    })


# En intranet/views.py

@login_required
def index(request):
    """ Index """
    form = ActividadForm
    if request.user.is_superuser:
        crear_cajas_chicas_faltantes()

    try:
        tracker = Actividad.objects.get(user=request.user, fin=None)
    except Actividad.DoesNotExist:
        tracker = None

    if tracker:
        ribbon = Expediente.objects.filter(
            ot=tracker.ot).order_by('-id').first()

        # Sumamos el tiempo de todas las veces anteriores que trabajó en ESTA misma tarea
        actividades_previas = Actividad.objects.filter(
            user=request.user,
            ot=tracker.ot,
            tarea=tracker.tarea,  # Misma tarea
            fin__isnull=False    # Solo las finalizadas/pausadas
        )

        acumulado_segundos = 0
        for act in actividades_previas:
            if act.inicio and act.fin:
                acumulado_segundos += (act.fin - act.inicio).total_seconds()

        tiempo_acumulado = int(acumulado_segundos)
        # ----------------------------------------------------
    else:
        ribbon = None
        tiempo_acumulado = 0  # Si no hay actividad, es 0

    context = {
        'tracker': tracker,
        'ribbon': ribbon,
        'form': form,
        # <--- [IMPORTANTE] Pasar esto al template
        'tiempo_acumulado': tiempo_acumulado
    }
    return render(request, 'index.html', context)


def end_actividad(request):
    """Finalizar Actividad"""
    if request.method == 'POST':
        id = request.POST.get('id')
        com_act = request.POST.get('comentario')
        try:
            actividades = Actividad.objects.get(id=id)
            actividades.comentario = com_act
            actividades.fin = timezone.now()
            actividades.save()
            messages.success(request, "Actividad finalizada con exito")
        except Exception:
            messages.error(request, "Error")
        return redirect('index')


@login_required
def proyectos(request):
    """ Proyectos """
    if request.method == 'POST':
        tipo_proyecto_id = request.POST.get('txtTipoProyecto', None)
        tipo_proyecto = TipOt.objects.get(
            id=tipo_proyecto_id) if tipo_proyecto_id else None
        try:
            nac_ot_str = request.POST.get('txtFecha', None)

            descripcion_data = request.POST.get('txtDescripcion', None)

            ot = Ot(
                id=request.POST.get('txtOT', None),
                nombre=request.POST.get('txtProyecto', None),
                color=request.POST.get('txtColor', None),
                inicio=nac_ot_str,
                id_tipot=tipo_proyecto,
                descripcion=descripcion_data  # 2. Añadimos el campo aquí
            )
            ot.save()

            messages.success(request, "OT y sus ingresos creados con éxito.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        return redirect('proyecto_detalle', id=ot.id)

    tipos_proyecto = TipOt.objects.all().order_by('nom_tipo')
    ots_list = Ot.objects.all()
    ots = []

    for ot in ots_list:
        expediente = Expediente.objects.filter(
            ot=ot.id).order_by('-id').first()
        ot.expediente = expediente
        ots.append(ot)

    context = {
        'ots': ots,
        'tipos_proyecto': tipos_proyecto,
        'today': date.today(),  # esto pasa la fecha de hoy al template
    }
    return render(request, 'proyectos.html', context)


def edit_proyecto(request, id):
    """ Editar Proyecto """
    ot = get_object_or_404(Ot, id=id)
    if request.method == 'POST':
        nombre = request.POST.get('txtNombre')
        estado = request.POST.get('sltEstado')
        color = request.POST.get('color')
        descripcion = request.POST.get('txtDescripcion', '')
        privado = int(request.POST.get('chkPrivado', 0))
        try:
            ot.nombre = nombre
            ot.estado = estado
            ot.color = color
            ot.descripcion = descripcion
            ot.privado = privado
            ot.save()
            messages.success(request, "OT editado con éxito")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        return redirect('proyecto_detalle', id=id)


def delete_proyecto(request):
    """Eliminar Proyecto"""
    if request.method == 'POST':
        id = request.POST.get('id', None)
        try:
            ot = Ot.objects.get(id=id)
            ot.delete()
            messages.success(request, "OT eliminado con éxito")
        except Ot.DoesNotExist:
            messages.error(request, "OT no encontrado")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        return redirect('proyectos')


@login_required
def proyecto_detalle(request, id):
    """ Proyectos Detalle """
    ot = Ot.objects.get(pk=id)
    form = TareaForm()
    gastos = Gasto.objects.filter(ot_id=id)
    total_gastos = gastos.aggregate(total=Sum('monto'))['total'] or 0
    expedientes_list = Expediente.objects.filter(
        ot=ot).order_by('-id')
    etiquetas = ot.etiquetas.all()
    actividades = Actividad.objects.filter(ot_id=id)
    total_timedelta = timedelta()

    # Cálculo de horas
    for act in actividades:
        if act.inicio and act.fin:
            hora_limite = act.inicio.replace(
                hour=8, minute=0, second=0, microsecond=0)
            inicio = act.inicio if act.inicio >= hora_limite else hora_limite
            diferencia = act.fin - inicio
            total_timedelta += diferencia

    total_horas = int(total_timedelta.total_seconds() // 3600)
    total_minutos = int((total_timedelta.total_seconds() % 3600) // 60)
    total_horas_registradas = f"{total_horas:02}:{total_minutos:02}"

    # --- NUEVO: OBTENER EL ÁREA DEL USUARIO ---
    nombre_area = ""
    try:
        # Buscamos al colaborador conectado (request.user)
        colaborador = Colaborador.objects.get(user=request.user)
        if colaborador.area:
            nombre_area = colaborador.area.nombre
    except Colaborador.DoesNotExist:
        pass

    context = {
        'form': form,
        'ot': ot,
        'gastos': gastos,
        'total_gastos': total_gastos,
        'total_horas_registradas': total_horas_registradas,
        'expedientes_list': expedientes_list,
        'nombre_area': nombre_area,
        'etiquetas': etiquetas,
    }
    return render(request, 'proyecto_detallado.html', context)


def chart_combinado(request):
    """
    API Real: Devuelve bloques de tiempo normalizados para vista semanal.
    X = Día de la semana (Lunes, Martes...)
    Y = Hora del día (Normalizada a una fecha fija para que se alineen)
    """
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    search_value = request.GET.get('search[value]', '').strip()

    data = []

    DUMMY_DATE = date(2000, 1, 1)

    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)

            queryset = Actividad.objects.filter(
                inicio__gte=start_date,
                inicio__lte=end_date,
                fin__isnull=False
            ).select_related('user', 'tarea').order_by('user__username', 'inicio')

            if search_value:
                queryset = queryset.filter(
                    Q(user__username__icontains=search_value) |
                    Q(comentario__icontains=search_value) |
                    Q(tarea__titulo__icontains=search_value)
                )

            actividades_por_usuario = {}
            for act in queryset:
                username = act.user.username
                if username not in actividades_por_usuario:
                    actividades_por_usuario[username] = []
                actividades_por_usuario[username].append(act)

            dias_es = {0: 'Lun', 1: 'Mar', 2: 'Mié',
                       3: 'Jue', 4: 'Vie', 5: 'Sáb', 6: 'Dom'}

            for username, actividades in actividades_por_usuario.items():
                last_end = None

                for act in actividades:
                    dia_semana = dias_es[act.inicio.weekday()]
                    dia_numero = act.inicio.strftime('%d')
                    x_label = f"{dia_semana} {dia_numero}"

                    inicio_normalizado = datetime.combine(
                        DUMMY_DATE, act.inicio.time())
                    fin_normalizado = datetime.combine(
                        DUMMY_DATE, act.fin.time())

                    if last_end:
                        if act.inicio.date() == last_end.date():
                            diferencia = act.inicio - last_end
                            if diferencia.total_seconds() > 60:
                                last_end_norm = datetime.combine(
                                    DUMMY_DATE, last_end.time())
                                data.append({
                                    'x': x_label,
                                    'y': [
                                        int(last_end_norm.timestamp() * 1000),
                                        int(inicio_normalizado.timestamp() * 1000)
                                    ],
                                    'fillColor': '#FF4560',
                                    'meta': 'Tiempo Muerto',
                                    'usuario': username
                                })
                        else:
                            last_end = None

                    titulo_tarea = act.tarea.titulo if act.tarea else (
                        act.descripcion or "Sin título")
                    data.append({
                        'x': x_label,
                        'y': [
                            int(inicio_normalizado.timestamp() * 1000),
                            int(fin_normalizado.timestamp() * 1000)
                        ],
                        'fillColor': '#00E396',  # Verde
                        'meta': titulo_tarea,
                        'usuario': username
                    })

                    last_end = act.fin

        except Exception as e:
            print(f"Error chart_combinado: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse(data, safe=False)
