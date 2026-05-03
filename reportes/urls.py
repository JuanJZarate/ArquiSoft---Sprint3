from django.urls import path
from .views import generar_reporte_finops
from .views import generar_reporte_finops, monitoreo_infra

urlpatterns = [
    path('generar-reporte/<int:usuario_id>/<int:proyecto_id>/', generar_reporte_finops),
    path('monitoreo/<int:usuario_id>/<int:proyecto_id>/', monitoreo_infra),
]

