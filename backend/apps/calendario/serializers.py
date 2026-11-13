from rest_framework import serializers
from .models import Evento, Recordatorio


class CalendarioSerializer(serializers.Serializer):
    """Serializer para visualizar en el calendario (GET)"""
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    start = serializers.CharField()
    end = serializers.CharField(required=False, allow_blank=True)
    ot = serializers.CharField(required=False, allow_blank=True)
    usuario = serializers.CharField(required=False, allow_blank=True)
    descripcion = serializers.CharField(required=False, allow_blank=True)
    allDay = serializers.BooleanField()
    className = serializers.CharField()
    recordatorio = serializers.IntegerField(required=False, allow_null=True)


class RecordatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recordatorio
        fields = ['cantidad', 'unidad']


class EventoSerializer(serializers.ModelSerializer):
    """Serializer para guardar/editar eventos (POST/PUT)"""
    recordatorios = RecordatorioSerializer(many=True, required=False)

    class Meta:
        """Meta clase para el serializer """
        model = Evento
        fields = '__all__'

    def create(self, validated_data):
        recordatorios_data = validated_data.pop('recordatorios', [])
        participantes_data = validated_data.pop('participantes', [])

        evento = Evento.objects.create(**validated_data)

        if participantes_data:
            evento.participantes.set(participantes_data)

        recordatorios_crear = [
            Recordatorio(evento=evento, **req_data) for req_data in recordatorios_data
        ]
        Recordatorio.objects.bulk_create(recordatorios_crear)

        return evento

    def update(self, instance, validated_data):
        recordatorios_data = validated_data.pop('recordatorios', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if recordatorios_data is not None:
            instance.recordatorios.all().delete()
            recordatorios_actualizar = [
                Recordatorio(evento=instance, **req_data) for req_data in recordatorios_data
            ]
            Recordatorio.objects.bulk_create(recordatorios_actualizar)
        return instance
