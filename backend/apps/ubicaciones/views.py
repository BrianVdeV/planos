"""Ubicaciones Views"""
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.html import escape
from django.views.generic import View
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend

from intranet.models import Ot

from .forms import UbicacionForm
from .models import Ubicacion, Ubigeo
from .serializers import UbicacionSerializer, UbigeoSerializer


class MapaView(LoginRequiredMixin, View):
    """Vista para listar ubicaciones"""

    def get(self, request):
        context = {
            'ots': Ot.objects.filter(estado='Activo')
        }
        return render(request, 'ubicaciones.html', context)

    def post(self, request):
        form = UbicacionForm(request.POST)
        print("Datos recibidos:", request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ubicación guardada exitosamente")
        else:
            messages.error(request, "Error al guardar la ubicación")
        return redirect('mapa')


class UbigeoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para los ubigeos"""
    queryset = Ubigeo.objects.order_by('id')
    serializer_class = UbigeoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['departamento', 'provincia', 'distrito']

    @action(detail=False, methods=['get'])
    def departamentos(self, request):
        """Devuelve la lista de departamentos"""
        departamentos = Ubigeo.objects.values_list(
            'departamento', flat=True).distinct()
        return Response(departamentos)

    @action(detail=False, methods=['get'])
    def provincias(self, request):
        """Devuelve la lista de provincias"""
        dep = request.query_params.get('departamento')
        provincias = Ubigeo.objects.filter(departamento=dep).values_list(
            'provincia', flat=True).distinct()
        return Response(provincias)


class UbicacionViewSet(viewsets.ModelViewSet):
    queryset = Ubicacion.objects.all().select_related('ot', 'ubigeo')
    serializer_class = UbicacionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter,
                       OrderingFilter, DatatablesFilterBackend]
    filterset_fields = ['ot', 'ubigeo__departamento',
                        'ubigeo__provincia', 'ubigeo__distrito']
    search_fields = ['numero', 'presentante', 'ot__nombre']
    ordering_fields = ['ot__id', 'presentacion', 'vencimiento']

    @action(detail=False, methods=['get'])
    def kml(self, request):
        """Devuelve las ubicaciones agrupadas por Año, Estado y con colores de pin"""
        ubicaciones = self.filter_queryset(
            self.get_queryset()).order_by('-ot__inicio')

        # 1. Definimos los Estilos (Styles) globales al principio del Documento
        kml_header = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
            <name>Proyectos Planos Perú</name>
            <open>1</open>
            
            <!-- Definición de Estilos de Pines -->
            <Style id="estilo_Activo">
            <IconStyle>
                <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
                </Icon>
            </IconStyle>
            </Style>
            
            <Style id="estilo_Finalizado">
            <IconStyle>
                <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/grn-pushpin.png</href>
                </Icon>
            </IconStyle>
            </Style>
            
            <Style id="estilo_Suspendido">
            <IconStyle>
                <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href>
                </Icon>
            </IconStyle>
            </Style>
            
            <Style id="estilo_Fallido">
            <IconStyle>
                <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href>
                </Icon>
            </IconStyle>
            </Style>
            
            <Style id="estilo_Desconocido">
            <IconStyle>
                <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png</href>
                </Icon>
            </IconStyle>
            </Style>
            """
        kml_footer = """  </Document>\n</kml>"""

        activos_por_ano = defaultdict(list)
        archivados_por_ano = defaultdict(list)

        # ... (la misma lógica de clasificación por año de la respuesta anterior) ...
        for ubi in ubicaciones:
            if not ubi.coordenadas:
                continue

            if ubi.ot and ubi.ot.inicio:
                ano = ubi.ot.inicio.year
            else:
                ano = "Sin Fecha"

            estado = ubi.ot.estado if ubi.ot else "Desconocido"

            if estado == 'Activo':
                activos_por_ano[ano].append(ubi)
            else:
                archivados_por_ano[ano].append(ubi)

        carpetas_kml = ""

        # 2. Actualizamos la función auxiliar para asignar el styleUrl correcto
        def generar_placemarks(lista_ubicaciones):
            html = ""
            for u in lista_ubicaciones:
                try:
                    lat, lng = u.coordenadas.split(',')
                    direccion_segura = escape(u.direccion)
                    estado_ot = escape(u.ot.estado) if u.ot else "Desconocido"

                    # Generamos un ID de estilo que coincida con los que definimos arriba
                    style_id = f"#estilo_{estado_ot}"

                    desc_html = escape(
                        f"<b>OT:</b> {u.ot.id}-{u.ot.nombre}<br><b>Distrito:</b> {u.ubigeo.distrito}<br><b>Dirección:</b> {direccion_segura}<br><b>Estado:</b> {estado_ot}")

                    html += f"""
      <Placemark>
        <name>{u.ot.id}</name>
        <styleUrl>{style_id}</styleUrl>  <!-- Aquí aplicamos el color -->
        <description>{desc_html}</description>
        <Point>
          <coordinates>{lng.strip()},{lat.strip()},0</coordinates>
        </Point>
      </Placemark>"""
                except ValueError:
                    continue
            return html

        # ... (el resto del código para generar las carpetas de Activos y Archivados sigue igual) ...
        anos_activos = sorted(
            [y for y in activos_por_ano.keys() if isinstance(y, int)], reverse=True)
        if "Sin Fecha" in activos_por_ano:
            anos_activos.append("Sin Fecha")

        for ano in anos_activos:
            carpetas_kml += f"""
    <Folder>
      <name>{ano} - Activos ({len(activos_por_ano[ano])})</name>
      <open>0</open>"""
            carpetas_kml += generar_placemarks(activos_por_ano[ano])
            carpetas_kml += """
    </Folder>"""

        if archivados_por_ano:
            carpetas_kml += """
    <Folder>
      <name>Archivado</name>
      <open>0</open>"""

            anos_archivados = sorted(
                [y for y in archivados_por_ano.keys() if isinstance(y, int)], reverse=True)
            if "Sin Fecha" in archivados_por_ano:
                anos_archivados.append("Sin Fecha")

            for ano in anos_archivados:
                carpetas_kml += f"""
      <Folder>
        <name>{ano} ({len(archivados_por_ano[ano])})</name>
        <open>0</open>"""
                carpetas_kml += generar_placemarks(archivados_por_ano[ano])
                carpetas_kml += """
      </Folder>"""

            carpetas_kml += """
    </Folder>"""

        kml_content = kml_header + carpetas_kml + kml_footer

        response = HttpResponse(
            kml_content, content_type='application/vnd.google-earth.kml+xml'
        )
        response['Content-Disposition'] = 'attachment; filename="ubicaciones_planos_peru.kml"'

        return response

    @action(detail=False, methods=['get'])
    def geojson(self, request):
        """Devuelve TODAS las ubicaciones en formato GeoJSON"""
        queryset = self.filter_queryset(self.get_queryset())
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        for ubicacion in queryset:
            coordenadas_geojson = None
            if ubicacion.coordenadas:
                try:
                    partes = ubicacion.coordenadas.split(',')
                    lat = float(partes[0].strip())
                    lng = float(partes[1].strip())
                    coordenadas_geojson = [lng, lat]
                except (ValueError, IndexError):
                    pass

            if coordenadas_geojson:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": coordenadas_geojson
                    },
                    "properties": {
                        "id": ubicacion.id,
                        "ot": ubicacion.ot_id,
                        "direccion": ubicacion.direccion,
                        "departamento": ubicacion.ubigeo.departamento if ubicacion.ubigeo else "",
                        "provincia": ubicacion.ubigeo.provincia if ubicacion.ubigeo else "",
                        "distrito": ubicacion.ubigeo.distrito if ubicacion.ubigeo else ""
                    }
                }
                geojson["features"].append(feature)

        return Response(geojson)
