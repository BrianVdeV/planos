from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Area, Colaborador


class ColaboradorSerializer(serializers.ModelSerializer):
    """Serializer"""
    area_nombre = serializers.CharField(source='area.nombre', read_only=True, default=None)

    class Meta:
        """Meta"""
        model = Colaborador
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Serializer"""
    colaborador = serializers.SerializerMethodField()

    class Meta:
        """Meta"""
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'is_superuser', 'colaborador']

    def get_colaborador(self, obj):
        try:
            colaborador = Colaborador.objects.select_related('area').get(user=obj)
            return ColaboradorSerializer(colaborador, context=self.context).data
        except Colaborador.DoesNotExist:
            return None


class Select2Serializer(serializers.ModelSerializer):
    """Serializer para los select2"""
    foto = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'foto']

    def get_foto(self, obj):
        # 1. Verificamos si el usuario tiene un perfil de 'colaborador'
        if hasattr(obj, 'colaborador') and obj.colaborador.foto:
            # 2. Retornamos la URL absoluta de la foto
            request = self.context.get('request')
            foto_url = obj.colaborador.foto.url
            if request:
                return request.build_absolute_uri(foto_url)
            return foto_url
        return None


class AreaSerializer(serializers.ModelSerializer):
    """Serializer"""
    class Meta:
        """Meta"""
        model = Area
        fields = '__all__'
