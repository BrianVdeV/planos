"""URL"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'expedientes', views.ExpedienteViewSet, 'expedientes')
router.register(r'sunarp', views.SunarpViewSet, 'sunarp')
router.register(r'municipalidad', views.MunicipalidadViewSet, 'municipalidad')


urlpatterns = [
    path('api/', include(router.urls)),
    path('expedientes/', views.expedientes, name='expedientes'),
    path('municipalidad-otros/', views.municipalidad_otros_view,
         name='municipalidad_otros'),
]
