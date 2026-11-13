"""URL"""
from django.urls import path, include
from rest_framework import routers
from intranet import views, api

router = routers.DefaultRouter()
router.register(r'ots', api.OtViewSet, 'ots')
router.register(r'ot-list', api.OTListAPIView, 'ot-list')
router.register(r'tipot', api.TipOtViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/chart/', api.ChartView.as_view(), name='chart'),
    path('api/chart-combinado/', views.chart_combinado, name='chart_combinado'),
    path('api/jquery-toast/', api.JqueryToastView.as_view(),
         name='notificaciones-toast'),
    path('api/notificaciones/', api.NotificacionesView.as_view(),
         name='notificaciones'),
    path('actividades/', views.index, name='index'),
    path('actividades/api/', views.end_actividad, name='end_actividad'),
    path('proyectos/', views.proyectos, name='proyectos'),
    path('proyectos/edit/<int:id>/',
         views.edit_proyecto, name='edit_proyecto'),
    path('proyectos/delete', views.delete_proyecto, name='delete_proyecto'),
    path('proyectos/<int:id>/', views.proyecto_detalle, name='proyecto_detalle'),
    path('sidebar', api.SidebarView.as_view(), name="sidebar"),
    path('index/api/', views.list_actividades_index,
         name='obtener_actividades_index'),
]
