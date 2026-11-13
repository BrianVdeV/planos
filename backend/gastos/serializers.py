""" Serializers para las clases de la aplicación gastos """
from decimal import Decimal
from rest_framework import serializers
from .models import Gasto, ReporteGasto, Saldo, Contrato


class GastoSerializer(serializers.ModelSerializer):
    """ Serializer para la clase Gasto """
    DT_RowId = serializers.SerializerMethodField()
    ot_str = serializers.CharField(source="ot", read_only=True)
    fecha = serializers.DateField(source='reporte.fecha', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        """ Meta clase para el serializer """
        model = Gasto
        fields = ['id', 'DT_RowId', 'fecha', 'usuario_nombre', 'reporte',
                  'ot', 'ot_str', 'categoria', 'descripcion', 'monto', 'archivo']

    def get_DT_RowId(self, obj):
        return obj.id

    def get_usuario_nombre(self, obj):
        """ Devuelve el nombre de usuario si el gasto tiene un reporte asociado """
        if obj.reporte and obj.reporte.usuario:
            return obj.reporte.usuario.username
        return None


class ReporteGastoSerializer(serializers.ModelSerializer):
    """ Serializer para la clase ReporteGasto """
    DT_RowId = serializers.SerializerMethodField()
    usuario_str = serializers.CharField(
        source='usuario', read_only=True)
    saldo = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False)

    class Meta:
        """ Meta clase para el serializer """
        model = ReporteGasto
        fields = ['id', 'DT_RowId', 'usuario', 'usuario_str', 'fecha',
                  'total', 'saldo', 'estado_aprobacion', 'vuelto', 'monto_recibido', 'mensaje']

    def get_DT_RowId(self, obj):
        return obj.id


class CajaChicaSerializer(serializers.Serializer):
    """Serializers Caja Chica"""
    fecha_ingreso = serializers.DateField(source='fecha')
    saldo1 = serializers.DecimalField(
        max_digits=10, decimal_places=2, source='saldo_inicial')
    saldo2 = serializers.DecimalField(
        max_digits=10, decimal_places=2, source='total')
    ingreso = serializers.DecimalField(max_digits=10, decimal_places=2)
    totales = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    total1 = serializers.DecimalField(
        max_digits=10, decimal_places=2, source='saldo_actual')
    reportes = ReporteGastoSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        # Obtenemos la representación estándar del objeto
        representation = super().to_representation(instance)

        # Redondear todos los valores decimales a dos decimales
        for field in ['id', 'saldo1', 'saldo2', 'ingreso', 'totales', 'total1']:
            if field in representation:
                # Redondeamos el valor a 2 decimales y lo convertimos a string
                representation[field] = str(
                    Decimal(representation[field]).quantize(Decimal('0.01')))

        return representation


class SaldoSerializer(serializers.ModelSerializer):
    """ Serializer para la clase Saldo """
    username = serializers.SerializerMethodField()

    class Meta:
        """ Meta clase para el serializer """
        model = Saldo
        fields = ['id', 'usuario', 'username',
                  'saldo_actual', 'saldo_inicial', 'fecha']

    def get_username(self, obj):
        """Método para obtener el nombre de usuario del usuario relacionado"""
        return obj.usuario.username


class ContratoSerializer(serializers.ModelSerializer):
    """ Serializer para la clase Contrato """
    class Meta:
        """ Meta clase para el serializer """
        model = Contrato
        fields = '__all__'
