from django.db import models
from autenticacion_usuarios.models import Usuario
from productos.models import Categoria


# ==========================================================
# MODELOS PARA CU14-CU20: REPORTES DINÁMICOS
# ==========================================================

class ModeloIA(models.Model):
    """Modelo para almacenar información de modelos de IA entrenados"""
    ESTADOS_MODELO = [
        ('activo', 'Activo'),
        ('entrenando', 'Entrenando'),
        ('retirado', 'Retirado'),
        ('error', 'Error'),
    ]
    
    id_modelo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    algoritmo = models.CharField(max_length=50)  # random_forest, linear_regression, etc.
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True)
    r2_score = models.FloatField(null=True, blank=True)  # Métrica de rendimiento
    rmse = models.FloatField(null=True, blank=True)  # Root Mean Squared Error
    ruta_modelo = models.CharField(max_length=500, blank=True, null=True)  # Ruta al archivo del modelo
    estado = models.CharField(max_length=20, choices=ESTADOS_MODELO, default='activo')
    version = models.CharField(max_length=20, default='1.0')
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'modelo_ia'
        verbose_name = 'Modelo de IA'
        verbose_name_plural = 'Modelos de IA'
        ordering = ['-fecha_entrenamiento']
    
    def __str__(self):
        return f"{self.nombre} v{self.version} - {self.get_estado_display()}"


class PrediccionVenta(models.Model):
    """Modelo para almacenar predicciones de ventas generadas por IA"""
    id_prediccion = models.AutoField(primary_key=True)
    fecha_prediccion = models.DateField()
    valor_predicho = models.DecimalField(max_digits=10, decimal_places=2)
    modelo_version = models.CharField(max_length=20, default='1.0')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_categoria')
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(ModeloIA, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_modelo')
    confianza = models.FloatField(default=0.0)  # Nivel de confianza de la predicción (0-1)
    
    class Meta:
        db_table = 'prediccion_venta'
        verbose_name = 'Predicción de Venta'
        verbose_name_plural = 'Predicciones de Venta'
        ordering = ['-fecha_ejecucion']
    
    def __str__(self):
        cat = self.categoria.nombre if self.categoria else "General"
        return f"Predicción {self.fecha_prediccion} - {cat} - ${self.valor_predicho}"


class Reporte(models.Model):
    """Modelo para reportes dinámicos generados"""
    TIPOS_REPORTE = [
        ('ventas', 'Ventas'),
        ('productos', 'Productos'),
        ('clientes', 'Clientes'),
        ('inventario', 'Inventario'),
        ('financiero', 'Financiero'),
        ('general', 'General'),
    ]
    
    FORMATOS_REPORTE = [
        ('pantalla', 'Pantalla'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
    ]
    
    ORIGENES_COMANDO = [
        ('texto', 'Texto'),
        ('voz', 'Voz'),
        ('manual', 'Manual'),
    ]
    
    id_reporte = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, choices=TIPOS_REPORTE)
    descripcion = models.TextField(blank=True, null=True)
    parametros = models.JSONField(default=dict, blank=True)  # Parámetros usados para generar el reporte
    prompt = models.TextField(blank=True, null=True)  # Texto original de la solicitud
    formato = models.CharField(max_length=20, choices=FORMATOS_REPORTE, default='pantalla')
    origen_comando = models.CharField(max_length=20, choices=ORIGENES_COMANDO, default='manual')
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_usuario')
    ruta_archivo = models.CharField(max_length=500, blank=True, null=True)  # Ruta al archivo generado (PDF/Excel)
    datos = models.JSONField(default=dict, blank=True)  # Datos del reporte en formato JSON
    filtros_aplicados = models.JSONField(default=dict, blank=True)  # Filtros aplicados
    estado = models.CharField(max_length=20, default='completado')  # completado, procesando, error
    
    class Meta:
        db_table = 'reporte'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_display()} - {self.fecha_generacion.strftime('%Y-%m-%d')}"
