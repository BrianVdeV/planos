"""Serializer"""
from rest_framework import serializers
from .models import Ubigeo, Ubicacion


class UbigeoSerializer(serializers.ModelSerializer):
    """Serializer para la clase Ubigeo"""
    class Meta:
        """ Meta clase para el serializer """
        model = Ubigeo
        fields = '__all__'


class UbicacionSerializer(serializers.ModelSerializer):
    """Serializer para Ubicacion con formato GeoJSON"""
    departamento = serializers.CharField(
        source='ubigeo.departamento', read_only=True)
    provincia = serializers.CharField(
        source='ubigeo.provincia', read_only=True)
    distrito = serializers.CharField(source='ubigeo.distrito', read_only=True)
    ubigeo_nombre = serializers.StringRelatedField(
        source='ubigeo', read_only=True)
    ot_str = serializers.StringRelatedField(source='ot', read_only=True)

    class Meta:
        model = Ubicacion
        fields = ['id', 'ot', 'ot_str', 'ubigeo', 'departamento', 'provincia', 'distrito',
                  'ubigeo_nombre', 'direccion', 'coordenadas']
