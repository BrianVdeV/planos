""" Serializers para las clases de la aplicación intranet """
from rest_framework import serializers
from .models import Etiqueta, Ot, TipOt


class EtiquetaSerializer(serializers.ModelSerializer):
    """Serializer para la clase Etiqueta"""
    badge = serializers.SerializerMethodField()

    class Meta:
        model = Etiqueta
        fields = ['id', 'nombre', 'color', 'badge']

    def get_badge(self, obj):
        return obj.badge_html()


class OtSerializer(serializers.ModelSerializer):
    """Serializer para la clase OT"""
    id_str = serializers.SerializerMethodField()

    class Meta:
        """ Meta clase para el serializer """
        model = Ot
        fields = '__all__'

    def get_id_str(self, obj):
        """ Método para obtener el id en formato string """
        return str(obj.id)+" - "+obj.nombre


class OtDataSerializer(serializers.ModelSerializer):
    id_str = serializers.SerializerMethodField()
    expediente_titles = serializers.SerializerMethodField()
    expediente_estado = serializers.SerializerMethodField()
    avance_estados = serializers.SerializerMethodField()
    gerente_username = serializers.SerializerMethodField()

    class Meta:
        model = Ot
        fields = [
            'id', 'id_str', 'color', 'inicio', 'estado', 'gerente_username',
            'expediente_titles', 'expediente_estado', 'privado', 'avance_estados',
        ]

    def get_avance_estados(self, obj):
        """Cálculo de porcentajes (sin tocar la BD)"""
        total = obj.total_t
        if total == 0:
            return {"todo": 0, "in_progress": 0, "review": 0, "done": 0, "total": 0}

        p_todo = round((obj.c_todo * 100.0) / total)
        p_prog = round((obj.c_progress * 100.0) / total)
        p_rev = round((obj.c_review * 100.0) / total)
        p_done = 100 - p_todo - p_prog - p_rev

        return {
            "todo": p_todo, "in_progress": p_prog,
            "review": p_rev, "done": p_done, "total": total
        }

    def get_id_str(self, obj):
        return f"{obj.id} - {obj.nombre}"

    def get_gerente_username(self, obj):
        return obj.gerente.username if obj.gerente else None

    def _get_primer_expediente(self, obj):
        """
        Helper para obtener el expediente más reciente desde la memoria
        """
        # Accedemos al atributo 'to_attr' definido en el Prefetch
        expedientes = getattr(obj, 'lista_expedientes', [])
        return expedientes[0] if expedientes else None

    def get_expediente_titles(self, obj):
        expediente = self._get_primer_expediente(obj)
        if expediente and expediente.presentacion:
            anio = expediente.presentacion.year
            return f"{anio}-{expediente.numero}"
        return None

    def get_expediente_estado(self, obj):
        expediente = self._get_primer_expediente(obj)
        return expediente.estado if expediente else None


class FeriadoSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    nombre = serializers.CharField(max_length=255)


class TipOtSerializer(serializers.ModelSerializer):
    """Serializer para la clase Tipo OT"""
    class Meta:
        """ Meta clase para el serializer """
        model = TipOt
        fields = '__all__'


class NotificacionesSerializers(serializers.Serializer):
    """Serializer para las notificaciones"""
    id = serializers.IntegerField()
    titulo = serializers.CharField(max_length=255)
    descripcion = serializers.CharField(max_length=500)
    fecha = serializers.DateTimeField()
    tipo = serializers.CharField(max_length=50)


class SidebarSerializer(serializers.Serializer):
    """Badges para sidebar"""
    agenda = serializers.IntegerField()
