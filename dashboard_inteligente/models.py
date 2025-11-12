from django.db import models
from django.utils import timezone
from reportes_dinamicos.models import ModeloIA

# ==========================================================
# MODELOS PARA CASOS DE USO DE IA
# ==========================================================
# Usamos el ModeloIA existente en reportes_dinamicos


class HistorialEntrenamiento(models.Model):
    """Historial de entrenamientos del modelo"""
    id_historial = models.AutoField(primary_key=True)
    modelo = models.ForeignKey(ModeloIA, on_delete=models.CASCADE, db_column='id_modelo')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('iniciado', 'Iniciado'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ], default='iniciado')
    registros_procesados = models.IntegerField(default=0)
    metricas = models.JSONField(default=dict, blank=True)  # Almacena métricas del entrenamiento
    mensaje_error = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'historial_entrenamiento'
        verbose_name = 'Historial de Entrenamiento'
        verbose_name_plural = 'Historiales de Entrenamiento'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Entrenamiento {self.modelo.nombre} - {self.fecha_inicio.strftime('%Y-%m-%d %H:%M')}"
