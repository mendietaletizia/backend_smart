from django.urls import path
from . import views

app_name = 'reportes_dinamicos'

urlpatterns = [
    # CU14-CU16: Solicitar e interpretar reportes
    path('solicitar/', views.SolicitarReporteView.as_view(), name='solicitar_reporte'),
    # CU17-CU20: Generar, descargar y visualizar reportes
    path('listar/', views.ListarReportesView.as_view(), name='listar_reportes'),
    path('<int:reporte_id>/descargar/', views.DescargarReporteView.as_view(), name='descargar_reporte'),
    # CU19: Filtros inteligentes
    path('filtros-inteligentes/', views.FiltrosInteligentesView.as_view(), name='filtros_inteligentes'),
    path('opciones-filtros/', views.OpcionesFiltrosView.as_view(), name='opciones_filtros'),
]

