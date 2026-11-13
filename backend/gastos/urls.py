from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'gastos', views.GastoViewSet, 'gastos')
router.register(r'saldos', views.SaldoViewSet, 'saldos')
router.register(r'reportes', views.ReporteGastoViewSet, 'reporte')
router.register(r'contratos', views.ContratoViewSet, 'contrato')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/cajachica/', views.CajaChicaAgrupadaView.as_view(),
         name='cajachica-list'),
    path('informes/gastos/', views.informes_gastos, name='informes_gastos'),
    path('gastos/', views.GastosView.as_view(), name='gastos'),
    path('aprobaciones/', views.aprobaciones, name='aprobaciones'),
    path('crear_gastos/', views.crear_gastos, name='crear_gastos'),
    path('guardar_gasto/', views.guardar_gasto, name='guardar_gasto'),
    path('gastos/editar_gastos/<int:reporte_id>/',
         views.editar_gastos, name='editar_gastos'),
    path('actualizar_gasto/', views.actualizar_gasto, name='actualizar_gasto'),
    path('registrar_caja_chica/', views.registrar_caja_chica,
         name='registrar_caja_chica'),
    path('verificar_caja_chica/', views.verificar_caja_chica,
         name='verificar_caja_chica'),
    path("editar_caja_chica/", views.editar_caja_chica, name="editar_caja_chica"),
    path('api/cajachica/<int:id>/', views.ActualizarIngresoView.as_view(),
         name='actualizar_ingreso'),
    path('exportar_cajachica_excel/', views.exportar_cajachica_excel,
         name='exportar_cajachica_excel'),
]
