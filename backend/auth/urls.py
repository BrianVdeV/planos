"""URL"""
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from auth import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, 'users')
router.register(r'area', views.AreaViewSet, 'area')
router.register(r'colaboradores', views.ColaboradorViewSet, 'colaboradores')

urlpatterns = [
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('equipo/', views.equipo_admin_view, name='equipo'),
    path('equipo/user', views.equipo_user_view, name='equipo_user'),
    path('equipo/add', views.add_equipo, name='add_equipo'),
    path('equipo/edit', views.edit_equipo, name='edit_equipo'),
    path("add_area/", views.add_area, name="add_area"),
    path("edit_area/", views.edit_area, name="edit_area"),
    path("delete_area/<int:id>/", views.delete_area, name="delete_area"),
    path('perfil/<int:id>/', views.perfil, name='perfil'),
    path('perfil-detalle/<int:id_user>/',
         views.perfil_detalle, name='perfil_detalle'),
    path("cambiar_contrasena/", views.cambiar_contrasena,
         name="cambiar_contrasena"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cambiar_estado/', views.cambiar_estado, name='cambiar_estado'),
    path('actualizar-perfil/<int:usuario_id>/',
         views.actualizar_perfil, name='actualizar_perfil'),
    path('actualizar-foto-perfil/<int:usuario_id>/',
         views.actualizar_foto_perfil, name='actualizar_foto_perfil'),
    path('check-username/', views.check_username, name='check-username'),
    path('cambiar-contrasena-equipo/<int:usuario_id>/',
         views.cambiar_contrasena_usuario, name='cambiar_contrasena_equipo'),
    path('actualizar-contrato/', views.actualizar_contrato,
         name='actualizar-contrato'),
    path('add-contrato/', views.add_contrato, name='add_contrato'),
]
