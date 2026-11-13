"""URL"""
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'ubigeo', views.UbigeoViewSet, 'ubigeo')
router.register(r'ubicacion', views.UbicacionViewSet, 'ubicacion')

urlpatterns = [
    path('api/', include(router.urls)),
    path('mapa/', views.MapaView.as_view(), name='mapa'),
]
