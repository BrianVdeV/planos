from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'cotizaciones', views.CotizacionViewSet,
                basename='cotizacion')

urlpatterns = [
    path('api/', include(router.urls)),
    path('cotizaciones/', views.cotizaciones_page_view, name='cotizaciones-list'),
]
