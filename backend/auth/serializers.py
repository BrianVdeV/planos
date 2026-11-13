from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Area, Colaborador


class UserSerializer(serializers.ModelSerializer):
    """Serializer"""
    colaborador = serializers.SerializerMethodField()

    class Meta:
        """Meta"""
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'colaborador']

    def get_colaborador(self, obj):
        try:
            colaborador = Colaborador.objects.get(user=obj)
            # Serializar los datos de Colaborador
            return ColaboradorSerializer(colaborador).data
        except Colaborador.DoesNotExist:
            return None  # Si el usuario no tiene colaborador, devolver None


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


class ColaboradorSerializer(serializers.ModelSerializer):
    """Serializer"""
    class Meta:
        """Meta"""
        model = Colaborador
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    """Serializer"""
    class Meta:
        """Meta"""
        model = Area
        fields = '__all__'
