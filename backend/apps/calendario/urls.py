from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/eventos/', views.EventoCreateAPIView.as_view(), name='evento-create'),
    path('api/calendario/', views.CalendarioView.as_view(), name='calendario-list'),
    path('calendario/', views.calendario, name='calendario'),
]
