import json
import os
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.expedientes.models import Expediente
from auth.models import Colaborador
from kanban.models import Tarea

from .forms import EventoForm
from .models import Evento
from .serializers import CalendarioSerializer, EventoSerializer

# Create your views here.


@login_required
def calendario(request):
    """Calendario"""
    form = EventoForm()
    context = {
        'form': form,
    }
    return render(request, 'calendario.html', context)


class EventoCreateAPIView(CreateAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer


class CalendarioView(APIView):
    """API Calendario (Visualización)"""

    def get(self, request):
        """Metodo GET"""
        calendario = []

        # 1. EVENTOS CREADOS POR USUARIOS
        eventos = Evento.objects.filter(estado='Activo').order_by('-id')
        for evento in eventos:
            nombres_participantes = ", ".join(
                [p.username for p in evento.participantes.all()])

            calendario.append({
                "id": evento.id,
                "title": evento.titulo,
                "start": evento.inicio,
                "end": evento.fin,
                "ot": str(evento.ot) if evento.ot else "",
                "usuario": nombres_participantes if nombres_participantes else None,
                "descripcion": evento.descripcion,
                "allDay": evento.allday,
                "className": "bg-primary",

                # 🔥 IMPORTANTE: Aquí enviamos el recordatorio al JS
                "recordatorio": None
            })

        # 2. EXPEDIENTES (Reingresos y Vencimientos)
        expedientes = Expediente.objects.filter(
            (Q(reingreso__isnull=False) | Q(vencimiento__isnull=False)) &
            ~Q(estado__in=['Inscrito', 'Tachado', 'En calificación'])
        ).order_by('-id')

        for expediente in expedientes:
            if expediente.reingreso:
                calendario.append({
                    "id": expediente.id,
                    "title": f"OT: {expediente.ot.id}",
                    "start": expediente.reingreso,
                    # Ajuste para evitar error si OT es null
                    "ot": expediente.ot.id if expediente.ot else "",
                    "descripcion": f"Estado: {expediente.estado}",
                    "allDay": True,
                    "className": "bg-warning",
                    "recordatorio": None  # No aplica
                })
            if expediente.vencimiento:
                calendario.append({
                    "id": expediente.id,
                    "title": f"OT {expediente.ot.id}",
                    "start": expediente.vencimiento,
                    "ot": expediente.ot.id if expediente.ot else "",
                    "descripcion": f"Estado: {expediente.estado}",
                    "allDay": True,
                    "className": "bg-danger",
                    "recordatorio": None
                })

        # 3. CUMPLEAÑOS
        cumples = Colaborador.objects.filter(user__is_active=True)
        anio_actual = datetime.now().year
        for cumple in cumples:
            if cumple.nacimiento:
                try:
                    fecha_cumple = datetime(
                        anio_actual, cumple.nacimiento.month, cumple.nacimiento.day)
                    calendario.append({
                        "id": cumple.id,
                        "title": f"🎂 {cumple.user}",
                        "start": fecha_cumple.strftime("%Y-%m-%d"),
                        "usuario": cumple.user.username,
                        "descripcion": f"Cumpleaños de {cumple.user}",
                        "allDay": True,
                        "className": "bg-info",
                        "recordatorio": None
                    })
                except ValueError:
                    pass  # Manejo para años bisiestos (29 feb)

        # 4. FERIADOS (JSON Estático)
        feriados_path = os.path.join(
            settings.BASE_DIR, 'static', 'docs', 'feriados.json')
        if os.path.exists(feriados_path):
            with open(feriados_path, encoding='utf-8') as f:
                feriados = json.load(f)
                for feriado in feriados:
                    date = feriado.get("date")
                    name = feriado.get("name")
                    if date:
                        calendario.append({
                            "id": "1",  # ID genérico
                            "title": f"🌞 {name}",
                            "start": date,
                            "descripcion": name,
                            "allDay": True,
                            "className": "bg-secondary",
                            "recordatorio": None
                        })

        # 5. TAREAS KANBAN (High Priority)
        tareas = Tarea.objects.filter(
            vencimiento__isnull=False,
            prioridad='high',
            estado__in=['todo', 'in_progress']
        )
        for tarea in tareas:
            calendario.append({
                "id": tarea.id,
                "title": f"{tarea.ot.id if tarea.ot else 'S/N'} - {tarea.titulo}",
                "start": tarea.vencimiento,
                "ot": tarea.ot.id if tarea.ot else None,
                "descripcion": f"Tarea pendiente. Prioridad: {tarea.prioridad}",
                "allDay": True,
                "className": "bg-dark",
                "recordatorio": None
            })

        # 6. VACACIONES
        calendario.extend(self.get_vacaciones(request))

        serializer = CalendarioSerializer(calendario, many=True)
        return Response(serializer.data)

    def get_vacaciones(self, request):
        """Método auxiliar para calcular vacaciones"""

        # Solo superusuarios pueden ver vacaciones
        if not request.user.is_superuser:
            return []
        usuarios = User.objects.filter(is_active=True).exclude(id__in=[2])
        vacaciones = []

        # Usuarios con vacaciones manuales
        vacaciones_personalizadas = {
            1:  [("2025-05-15", "2025-05-22"), ("2026-02-09", "2026-02-15")],  # Jorge
            31: [("2025-10-20", "2025-10-27"), ("2026-01-02", "2026-01-09")],   # Betci
        }

        for user in usuarios:
            if not user.date_joined:
                continue

            fecha_inicio = user.date_joined.date()
            fechas_vacaciones = []
            num_vacaciones = 3 if user.id == 41 else 2

            if user.id in vacaciones_personalizadas:
                ult_fecha_manual = None
                for start, end in vacaciones_personalizadas[user.id]:
                    fechas_vacaciones.append((start, end))
                    ult_fecha_manual = datetime.strptime(
                        end, "%Y-%m-%d").date()

                fecha_vacaciones = ult_fecha_manual + \
                    timedelta(
                        days=180) if ult_fecha_manual else fecha_inicio + timedelta(days=180)
            else:
                fecha_vacaciones = fecha_inicio + timedelta(days=180)

            while len(fechas_vacaciones) < num_vacaciones:
                start_date = fecha_vacaciones
                end_date = start_date + timedelta(days=7)
                fechas_vacaciones.append((start_date.strftime(
                    "%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
                fecha_vacaciones += timedelta(days=180)

            for start, end in fechas_vacaciones:
                vacaciones.append({
                    "id": uuid.uuid4().int >> 64,
                    "username": user.username,
                    "title": f"🌴 {user.username} (Vacaciones)",
                    "start": start,
                    "end": end,
                    "descripcion": f"Vacaciones de {user.username} del {start} al {end}",
                    "usuario": user.username,
                    "allDay": True,
                    "className": "bg-success",
                    "backgroundColor": "#0acf97",
                    "borderColor": "#0acf97",
                    "textColor": "#fff",
                    "recordatorio": None
                })

        return vacaciones
