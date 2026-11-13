"""Dashboard Operativo: Vencimientos, Reingresos, Agenda y Actividad Reciente del Robot."""
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import F, Max
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.utils.timezone import now

from apps.calendario.models import Evento
from apps.expedientes.models import Expediente, HistorialSunarp


@login_required
def dashboard(request):
    """
    Dashboard Operativo: 
    Muestra Vencimientos, Reingresos, Agenda del día y Actividad Reciente del Robot.
    """
    if not (request.user.is_superuser or request.user.groups.filter(name='Ventas').exists()):
        return redirect('index')
    # -------------------------------------------------------------

    # 1. Fechas de referencia
    hoy = now().date()
    semana_proxima = hoy + timedelta(days=14)

    # ---------------------------------------------------------
    # A. KPI: ALERTAS DE VENCIMIENTOS (Expediente Sunarp)
    # ---------------------------------------------------------
    # Base: Sunarp, con fecha vencimiento y NO finalizados
    observados = Expediente.objects.filter(
        entidad='Sunarp',
        estado='Observado',
    )

    # Contadores para las tarjetas de arriba
    total_observados = observados.count()
    total_proximos = observados.filter(
        vencimiento__range=[hoy, semana_proxima]).count()

    # Lista para la Tabla "Próximos a Vencer" (Los 10 más urgentes)
    lista_urgentes = Expediente.objects.filter(
        entidad='Sunarp',
        estado__in=['Observado', 'Liquidado']
    ).annotate(
        fecha_final=Coalesce('reingreso', 'vencimiento')
    ).filter(
        fecha_final__lte=semana_proxima,
    ).select_related('ot').order_by('fecha_final')

    # ---------------------------------------------------------
    # B. KPI: REINGRESOS PENDIENTES
    # ---------------------------------------------------------
    apelados = Expediente.objects.filter(estado='Apelado')

    # ---------------------------------------------------------
    # C. AGENDA: EVENTOS DE HOY (Y PRÓXIMOS 7 DÍAS)
    # ---------------------------------------------------------
    eventos_hoy = Evento.objects.filter(
        # Rango: Hoy hasta semana próxima
        inicio__date__range=[hoy, semana_proxima]
    ).order_by('inicio')

    # ---------------------------------------------------------
    # D. TARJETA CENTRAL: HISTORIAL ROBOT (Último estado de cada expediente)
    # ---------------------------------------------------------
    historial_robot = HistorialSunarp.objects.filter(
        pk__in=HistorialSunarp.objects.values('expediente').annotate(
            max_fecha=Max('fecha_hora')
        ).values('expediente', 'max_fecha').filter(
            fecha_hora=F('max_fecha')
        ).values('pk')
    ).select_related('expediente', 'expediente__ot').order_by('-fecha_hora')[:10]

    # ---------------------------------------------------------
    # CONTEXTO FINAL
    # ---------------------------------------------------------
    context = {
        # Contadores
        'total_observados': total_observados,
        'total_proximos': total_proximos,
        'apelados': apelados,

        # Listas de datos
        'lista_urgentes': lista_urgentes,
        'eventos_hoy': eventos_hoy,
        'historial_robot': historial_robot,
    }

    return render(request, 'dashboard.html', context)


def dashboard_gastos(request):
    """ Dashboard """
    return render(request, 'dashboard_gastos.html')
