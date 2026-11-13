"""URL"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('api/', include(router.urls)),
    path('informe-promedio/', views.promedio, name='informe_promedio'),
    path('resumen/', views.resumen, name='resumen'),
    path('exportar_actividades_excel/', views.export_actividades_excel,
         name='exportar_actividades_excel'),
    path('exportar_resumen_excel/', views.export_resumen_excel,
         name='exportar_resumen_excel'),
    path('detallado/', views.detallado, name='detallado'),
    path('informes/actividades/', views.informes_actividades,
         name='informes_actividades'),
]
