"""Serializers"""
from django.utils.html import format_html
from rest_framework import serializers
from rest_framework.fields import DateField

from .models import Expediente, ExpedientePago


class ExpedienteSerializer(serializers.ModelSerializer):
    """ Serializer para la clase Expediente con soporte Datatables """

    DT_RowId = serializers.SerializerMethodField()
    ot_link = serializers.SerializerMethodField()
    ot_str = serializers.StringRelatedField(source='ot', read_only=True)
    expediente_str = serializers.SerializerMethodField()
    fecha_inicio_ot = serializers.SerializerMethodField()
    estado_badge = serializers.SerializerMethodField()
    anio = serializers.SerializerMethodField()

    class Meta:
        model = Expediente
        fields = (
            'DT_RowId', 'id', 'ot', 'ot_str', 'ot_link', 'fecha_inicio_ot',
            'entidad', 'oficina', 'presentante', 'presentacion', 'numero',
            'estado', 'estado_badge', 'expediente_str', 'anio',
            'reingreso', 'vencimiento', 'creado', 'editado'
        )
        datatables_always_serialize = ('id',)
        read_only_fields = ('creado', 'editado',)

    def get_DT_RowId(self, obj):
        return obj.id

    def get_fecha_inicio_ot(self, obj):
        if obj.ot and obj.ot.inicio:
            return obj.ot.inicio.strftime("%d/%m/%y")
        return "-"

    def get_anio(self, obj):
        """Año de presentación del expediente"""
        return obj.presentacion.year if obj.presentacion else "-"

    def get_ot_link(self, obj):
        if obj.ot:
            texto = f"{obj.ot.id} - {obj.ot.nombre}"
            return format_html("<b>{}</b>", texto)
        return "Sin OT"

    def get_estado_badge(self, obj):
        color = Expediente.get_color(obj.estado)
        return format_html('<span style="color: {};">{}</span>', color, obj.estado)

    def get_expediente_str(self, obj):
        return str(obj)


class ExpedienteListSerializer(serializers.ModelSerializer):
    """Muestra los expedientes para el detallado de actividades"""
    titulo = serializers.SerializerMethodField()
    reingreso = DateField(format="%d/%m/%y", required=False, allow_null=True)
    vencimiento = DateField(format="%d/%m/%y", required=False, allow_null=True)

    class Meta:
        model = Expediente
        fields = ['titulo', 'estado', 'reingreso', 'vencimiento']

    def get_titulo(self, obj):
        return str(obj)


class ExpedientePagoSerializer(serializers.ModelSerializer):
    """ Serializer para la clase ExpedientePago """
    class Meta:
        model = ExpedientePago
        fields = '__all__'
