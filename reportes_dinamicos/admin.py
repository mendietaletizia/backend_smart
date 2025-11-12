from django.contrib import admin
from .models import ModeloIA, PrediccionVenta, Reporte

@admin.register(ModeloIA)
class ModeloIAAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'version', 'algoritmo', 'estado', 'fecha_entrenamiento', 'r2_score')
    list_filter = ('estado', 'algoritmo')
    search_fields = ('nombre', 'version')
    readonly_fields = ('fecha_entrenamiento', 'fecha_ultima_actualizacion')

@admin.register(PrediccionVenta)
class PrediccionVentaAdmin(admin.ModelAdmin):
    list_display = ('fecha_prediccion', 'valor_predicho', 'categoria', 'modelo', 'confianza', 'fecha_ejecucion')
    list_filter = ('fecha_prediccion', 'categoria', 'modelo')
    search_fields = ('categoria__nombre',)

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'formato', 'estado', 'fecha_generacion', 'id_usuario')
    list_filter = ('tipo', 'formato', 'estado', 'fecha_generacion')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('fecha_generacion',)
