from django.contrib import admin
from .models import HistorialEntrenamiento

# ModeloIA está registrado en reportes_dinamicos.admin
# No lo registramos aquí para evitar duplicados

@admin.register(HistorialEntrenamiento)
class HistorialEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'fecha_inicio', 'fecha_fin', 'estado', 'registros_procesados')
    list_filter = ('estado', 'fecha_inicio')
    readonly_fields = ('fecha_inicio', 'fecha_fin', 'metricas')
