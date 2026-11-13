"""Serializer for Tarea model."""
from datetime import timedelta
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import DateTimeField
from apps.expedientes.serializers import ExpedienteListSerializer
from auth.serializers import Select2Serializer
from .models import Tarea, Actividad


class TareaSerializer(serializers.ModelSerializer):
    """Serializer for Tarea model."""
    ot_str = serializers.CharField(source="ot", read_only=True)
    duracion = serializers.SerializerMethodField()
    duracion_minutos = serializers.SerializerMethodField()
    duracion_input = serializers.CharField(write_only=True, required=False)
    horas_trabajadas = serializers.SerializerMethodField()
    participantes = serializers.SerializerMethodField()
    responsables_info = serializers.SerializerMethodField()

    class Meta:
        model = Tarea
        fields = [
            'id', 'ot', 'ot_str', 'titulo', 'descripcion',
            'estado', 'creado', 'prioridad', 'vencimiento',
            'duracion',
            'duracion_minutos',  # <--- AGREGA ESTO A LA LISTA DE CAMPOS
            'duracion_input', 'orden', 'participantes', 'horas_trabajadas',
            'responsables', 'responsables_info'
        ]
        read_only_fields = ['ot_str', 'responsables_info']

    def to_representation(self, instance):
        """Mostrar id, username y foto de los responsables"""
        response = super().to_representation(instance)
        response['responsables_info'] = Select2Serializer(
            instance.responsables.all(),
            many=True,
            context=self.context
        ).data
        return response

    def get_responsables_info(self, obj):
        return [user.username for user in obj.responsables.all()]

    def get_duracion(self, obj):
        """ Devuelve solo HH:MM para visualización """
        if obj.duracion:
            total_seconds = int(obj.duracion.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02}:{minutes:02}"
        return None

    # --- NUEVO MÉTODO PARA CALCULAR MINUTOS ---
    def get_duracion_minutos(self, obj):
        """Convierte el timedelta a un número entero de minutos para el input HTML"""
        if obj.duracion:
            return int(obj.duracion.total_seconds() // 60)
        return None
    # ------------------------------------------

    def get_horas_trabajadas(self, obj):
        qs = Actividad.objects.filter(tarea=obj, fin__isnull=False)
        qs = qs.annotate(tiempo=ExpressionWrapper(
            F("fin") - F("inicio"), output_field=DurationField()
        ))
        total = qs.aggregate(total=Sum("tiempo"))["total"]

        if total:
            horas = total.total_seconds() // 3600
            minutos = (total.total_seconds() % 3600) // 60
            return f"{int(horas):02}:{int(minutos):02}"
        return "00:00"

    def get_participantes(self, obj):
        from .models import Actividad
        users = (
            Actividad.objects.filter(tarea=obj, user__isnull=False)
            .values_list("user__username", flat=True)
            .distinct()
        )
        return list(users)

    def validate(self, data):
        duracion_str = data.pop("duracion_input", None)
        if duracion_str:
            try:
                hours, minutes = map(int, duracion_str.split(":"))
                data["duracion"] = timedelta(hours=hours, minutes=minutes)
            except ValueError:
                raise serializers.ValidationError(
                    "Formato de duración inválido. Usa hh:mm.")
        return data


class ActividadSerializer(serializers.ModelSerializer):
    """ Serializer principal para CRUD de Actividad """
    duracion_input = serializers.CharField(write_only=True, required=False)
    user_nombre = serializers.ReadOnlyField(source='user.username')
    tarea_nombre = serializers.ReadOnlyField(source='tarea.titulo')

    class Meta:
        model = Actividad
        fields = '__all__'

    def validate(self, attrs):
        """Validar para ingresar a tarea"""
        duracion_str = attrs.pop("duracion_input", None)
        if duracion_str:
            try:
                minutos_int = int(duracion_str)
                if minutos_int < 1:
                    raise serializers.ValidationError(
                        "Los minutos no pueden ser negativos ni cero.")
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    "Formato de duración inválido. Ingresa solo el número de minutos.")
        return attrs


class InformesSerializer(serializers.ModelSerializer):
    """Muestra los informes con cálculos de tiempos"""
    user = serializers.StringRelatedField()
    ot = serializers.StringRelatedField()
    tarea = serializers.StringRelatedField()
    tarea_estado = serializers.CharField(source='tarea.estado', read_only=True)
    comentario = serializers.SerializerMethodField()
    expedientes = ExpedienteListSerializer(
        many=True, read_only=True, source='ot.expedientes_set')

    # Campos existentes
    total = serializers.SerializerMethodField()
    total_decimal = serializers.SerializerMethodField()
    inicio = DateTimeField(format="%H:%M")
    fin = DateTimeField(format="%H:%M", allow_null=True)
    fecha = serializers.SerializerMethodField()

    # --- NUEVOS CAMPOS SOLICITADOS ---
    tiempo_estimado = serializers.SerializerMethodField()
    tiempo_desviacion = serializers.SerializerMethodField()
    tiempo_total_calculado = serializers.SerializerMethodField()

    class Meta:
        """Meta"""
        model = Actividad
        fields = [
            'id', 'user', 'ot', 'tarea', 'tarea_estado', 'comentario',
            'inicio', 'fin', 'fecha', 'expedientes',
            'total', 'total_decimal',
            # Agregamos los nuevos campos al array de fields
            'tiempo_estimado', 'tiempo_desviacion', 'tiempo_total_calculado',
            'pausado'
        ]

    def get_comentario(self, obj):
        """Devuelve el comentario en minúsculas."""
        if obj.comentario:
            return obj.comentario.lower()
        return None

    def get_fecha(self, obj):
        return obj.inicio.strftime("%d/%m/%y") if obj.inicio else None

    def get_total(self, obj):
        return obj.total()

    def get_total_decimal(self, obj):
        return obj.total_decimal()

    # --- FUNCIONES AUXILIARES Y NUEVOS CÁLCULOS ---

    def _format_timedelta(self, td):
        """Función auxiliar para formatear timedelta a HH:MM:SS"""
        if not td:
            return "00:00:00"
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def get_tiempo_estimado(self, obj):
        """ Calcula el tiempo estimado de la tarea asociada"""
        if obj.tarea and obj.tarea.duracion:
            duracion = obj.tarea.duracion
            return self._format_timedelta(duracion)
        return "0"

    def get_tiempo_desviacion(self, obj):
        """
        Calcula: Tiempo Real - Tiempo Estimado.
        Solo retorna valor si el Real es mayor al Estimado.
        """
        # 1. Obtener Estimado
        estimado = timedelta(0)
        if obj.tarea and obj.tarea.duracion and obj.tarea.duracion.total_seconds() > 0:
            estimado = obj.tarea.duracion

        # 2. Obtener Real
        if not obj.inicio:
            return "00:00:00"
        final = obj.fin if obj.fin else timezone.now()
        real = final - obj.inicio

        # 3. Calcular Diferencia
        if real > estimado:
            diferencia = real - estimado
            return self._format_timedelta(diferencia)

        return "00:00:00"

    def get_tiempo_total_calculado(self, obj):
        """
        Calcula el tiempo transcurrido real.
        Si la actividad no ha terminado, calcula hasta 'ahora'.
        """
        if not obj.inicio:
            return "00:00:00"

        final = obj.fin if obj.fin else timezone.now()
        # Asegurar que no sea negativo si hay desfase de hora
        if final < obj.inicio:
            return "00:00:00"

        tiempo_real = final - obj.inicio
        return self._format_timedelta(tiempo_real)
