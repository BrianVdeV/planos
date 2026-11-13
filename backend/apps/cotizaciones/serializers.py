from django.contrib.auth.models import User
from rest_framework import serializers
from intranet.models import TipOt
from .models import Cotizacion, Cancelacion


class CancelacionSerializer(serializers.ModelSerializer):
    """Cuotas de la cotizacion"""
    class Meta:
        model = Cancelacion
        fields = ['id', 'monto', 'descripcion', 'fecha']


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class CotizacionSerializer(serializers.ModelSerializer):
    """Cotizaciones"""
    user = UserSimpleSerializer(read_only=True)
    total = serializers.SerializerMethodField()
    cuotas = CancelacionSerializer(
        source='cancelacion_set', many=True, required=False)

    class Meta:
        model = Cotizacion
        fields = '__all__'

    def get_total(self, obj):
        return obj.total_cuotas()

    def update(self, instance, validated_data):
        if 'cancelacion_set' in validated_data:
            validated_data.pop('cancelacion_set')

        instance = super().update(instance, validated_data)
        cuotas_raw = self.context['request'].data.get('cuotas', [])

        for cuota_data in cuotas_raw:
            c_id = cuota_data.get('id')
            if c_id:
                try:
                    cuota_obj = Cancelacion.objects.get(
                        id=c_id, cotizacion=instance)
                    if 'fecha' in cuota_data:
                        cuota_obj.fecha = cuota_data['fecha']
                    if 'descripcion' in cuota_data:
                        cuota_obj.descripcion = cuota_data['descripcion']
                    if 'monto' in cuota_data:
                        cuota_obj.monto = cuota_data['monto']

                    cuota_obj.save()
                except Cancelacion.DoesNotExist:
                    pass

        return instance


class CotizacionCreateSerializer(serializers.ModelSerializer):
    cuotas = CancelacionSerializer(many=True)
    usuario_nombre = serializers.CharField(write_only=True)
    tipo_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)

    class Meta:
        model = Cotizacion
        fields = [
            'nombre', 'titulo', 'detalles', 'area', 'pisos', 'cliente', 'ubicacion',
            'telefono', 'dni', 'observaciones', 'elaboracion', 'estado',
            'usuario_nombre', 'tipo_id', 'cuotas'
        ]

    def create(self, validated_data):
        # Extraemos datos que no son campos directos del modelo Cotizacion
        cuotas_data = validated_data.pop('cuotas')
        username = validated_data.pop('usuario_nombre')
        tipo_id = validated_data.pop('tipo_id', None)

        # Buscamos al usuario
        try:
            user_instance = User.objects.get(username=username)
        except User.DoesNotExist:
            user_instance = User.objects.first()  # Fallback

        tipo_instance = None
        if tipo_id:
            try:
                tipo_instance = TipOt.objects.get(id=tipo_id)
            except TipOt.DoesNotExist:
                pass

        # Creamos la Cotización
        cotizacion = Cotizacion.objects.create(
            user=user_instance,
            tipo=tipo_instance,
            **validated_data
        )

        # Creamos las Cuotas asociadas
        for cuota in cuotas_data:
            Cancelacion.objects.create(
                cotizacion=cotizacion,
                monto=cuota['monto'],
                descripcion=cuota['descripcion'],
                fecha=cuota['fecha']
            )

        return cotizacion
