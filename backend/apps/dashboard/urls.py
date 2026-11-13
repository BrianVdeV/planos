from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.dashboard, name='dashboard_proyectos'),
    path('dashboard/gastos/', views.dashboard_gastos, name='dashboard_gastos'),
]
