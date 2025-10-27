# 🤖 Guía de Implementación de IA para SmartSales365

## 📋 Índice
1. [Configuración Inicial](#configuración-inicial)
2. [Estructura del Modelo](#estructura-del-modelo)
3. [Implementación del Modelo Random Forest](#implementación-del-modelo-random-forest)
4. [API de Predicciones](#api-de-predicciones)
5. [Integración con Dashboard](#integración-con-dashboard)

---

## 🚀 Configuración Inicial

### 1. Instalar Librerías Necesarias

Agregar al `requirements.txt`:

```txt
scikit-learn==1.5.1
joblib==1.4.0
pandas==2.2.0
numpy==1.26.3
```

Luego ejecutar:
```bash
pip install -r requirements.txt
```

### 2. Estructura de Carpetas

Crear la siguiente estructura en `dashboard_inteligente/`:

```
dashboard_inteligente/
├── models/
│   ├── __init__.py
│   ├── random_forest_model.py    # Clase del modelo
│   ├── data_preparation.py        # Preparación de datos
│   └── model_training.py          # Entrenamiento del modelo
├── serializers.py                  # Serializers para la API
├── views.py                        # Views de las APIs
├── urls.py                         # URLs del dashboard
└── tasks.py                        # Tareas periódicas (opcional)
```

---

## 🧠 Estructura del Modelo

### Dataset de Entrenamiento

Se necesitan al menos estos campos históricos de ventas:

```python
# Ejemplo de datos históricos necesarios
{
    'fecha': '2024-01-15',
    'producto_id': 1,
    'categoria_id': 1,
    'cantidad_vendida': 25,
    'precio_unitario': 150.00,
    'total_venta': 3750.00,
    'mes': 1,
    'dia_semana': 2,
    'es_fin_semana': False,
    'cliente_id': 123
}
```

### Características (Features) para el Modelo

```python
features = [
    'mes',
    'dia_semana', 
    'es_fin_semana',
    'categoria_id',
    'precio_unitario',
    'temporada'  # 1=Verano, 2=Otoño, 3=Invierno, 4=Primavera
]
```

---

## 📝 Implementación del Modelo Random Forest

### 1. Archivo: `dashboard_inteligente/models/random_forest_model.py`

```python
"""
Modelo Random Forest para predicción de ventas
"""
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from pathlib import Path
import os

class VentasRandomForestModel:
    """
    Modelo Random Forest para predecir ventas futuras
    """
    
    def __init__(self):
        self.model = None
        self.model_path = Path(__file__).parent.parent / 'models' / 'random_forest_model.joblib'
        
    def entrenar(self, datos_historicos):
        """
        Entrena el modelo con datos históricos
        
        Args:
            datos_historicos: DataFrame con datos de ventas históricas
        """
        # Preparar datos
        X, y = self.preparar_datos(datos_historicos)
        
        # Dividir en train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Crear y entrenar modelo
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"Modelo entrenado. MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        
        # Guardar modelo
        self.guardar()
        
        return {
            'mae': mae,
            'rmse': rmse
        }
    
    def preparar_datos(self, df):
        """
        Prepara los datos para el entrenamiento
        """
        # Convertir fecha
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Extraer características
        df['mes'] = df['fecha'].dt.month
        df['dia_semana'] = df['fecha'].dt.dayofweek
        df['es_fin_semana'] = df['fecha'].dt.dayofweek >= 5
        
        # Temporada (1-4)
        df['temporada'] = df['mes'].apply(self.asignar_temporada)
        
        # Seleccionar features
        features = ['mes', 'dia_semana', 'es_fin_semana', 'categoria_id', 
                   'precio_unitario', 'temporada']
        
        X = df[features]
        y = df['total_venta']
        
        return X, y
    
    def asignar_temporada(self, mes):
        """Asigna temporada según el mes"""
        if mes in [12, 1, 2]:
            return 3  # Verano (hemisferio sur)
        elif mes in [3, 4, 5]:
            return 4  # Otoño
        elif mes in [6, 7, 8]:
            return 1  # Invierno
        else:
            return 2  # Primavera
    
    def predecir(self, datos_futuros):
        """
        Hace predicciones con el modelo
        
        Args:
            datos_futuros: DataFrame con datos futuros para predecir
        
        Returns:
            Array con predicciones
        """
        if self.model is None:
            self.cargar()
        
        # Preparar datos futuros (similar a preparar_datos)
        datos_futuros['fecha'] = pd.to_datetime(datos_futuros['fecha'])
        datos_futuros['mes'] = datos_futuros['fecha'].dt.month
        datos_futuros['dia_semana'] = datos_futuros['fecha'].dt.dayofweek
        datos_futuros['es_fin_semana'] = datos_futuros['fecha'].dt.dayofweek >= 5
        datos_futuros['temporada'] = datos_futuros['mes'].apply(self.asignar_temporada)
        
        features = ['mes', 'dia_semana', 'es_fin_semana', 'categoria_id',
                   'precio_unitario', 'temporada']
        
        X = datos_futuros[features]
        predicciones = self.model.predict(X)
        
        return predicciones
    
    def guardar(self):
        """Guarda el modelo en disco"""
        self.model_path.parent.mkdir(exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Modelo guardado en: {self.model_path}")
    
    def cargar(self):
        """Carga el modelo desde disco"""
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            print(f"Modelo cargado desde: {self.model_path}")
        else:
            raise FileNotFoundError("No existe modelo guardado. Entrena primero.")
```

### 2. Archivo: `dashboard_inteligente/models/model_training.py`

```python
"""
Script para entrenar el modelo con datos históricos
"""
from .random_forest_model import VentasRandomForestModel
from ventas_carrito.models import Venta
from productos.models import Producto, Categoria
import pandas as pd

def obtener_datos_historicos(ultimos_meses=12):
    """
    Obtiene datos históricos de ventas de la base de datos
    """
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    fecha_inicio = timezone.now() - timedelta(days=30 * ultimos_meses)
    
    # Obtener ventas
    ventas = Venta.objects.filter(
        fecha__gte=fecha_inicio
    ).select_related('producto', 'cliente')
    
    # Convertir a DataFrame
    datos = []
    for venta in ventas:
        datos.append({
            'fecha': venta.fecha,
            'producto_id': venta.producto.id,
            'categoria_id': venta.producto.categoria.id,
            'cantidad_vendida': venta.cantidad,
            'precio_unitario': venta.precio_unitario,
            'total_venta': venta.total,
            'cliente_id': venta.cliente.id
        })
    
    df = pd.DataFrame(datos)
    return df

def entrenar_modelo():
    """
    Función principal para entrenar el modelo
    """
    # Obtener datos
    datos = obtener_datos_historicos()
    
    if len(datos) < 100:
        print("⚠️ Advertencia: Muy pocos datos históricos. Generando datos sintéticos...")
        datos = generar_datos_sinteticos()
    
    # Entrenar modelo
    modelo = VentasRandomForestModel()
    metricas = modelo.entrenar(datos)
    
    print("✅ Modelo entrenado exitosamente!")
    print(f"MAE: {metricas['mae']:.2f}")
    print(f"RMSE: {metricas['rmse']:.2f}")
    
    return modelo

def generar_datos_sinteticos(n=1000):
    """
    Genera datos sintéticos para entrenamiento inicial
    """
    import random
    from datetime import datetime, timedelta
    
    datos = []
    fecha_inicio = datetime.now() - timedelta(days=365)
    
    for i in range(n):
        fecha = fecha_inicio + timedelta(days=random.randint(0, 365))
        datos.append({
            'fecha': fecha,
            'producto_id': random.randint(1, 20),
            'categoria_id': random.randint(1, 5),
            'cantidad_vendida': random.randint(1, 50),
            'precio_unitario': round(random.uniform(10, 500), 2),
            'total_venta': round(random.uniform(50, 5000), 2),
            'cliente_id': random.randint(1, 50)
        })
    
    return pd.DataFrame(datos)

# Para ejecutar desde Django shell:
# python manage.py shell
# >>> from dashboard_inteligente.models.model_training import entrenar_modelo
# >>> modelo = entrenar_modelo()
```

---

## 🔌 API de Predicciones

### 1. Serializer: `dashboard_inteligente/serializers.py`

```python
"""
Serializers para el dashboard y predicciones
"""
from rest_framework import serializers
from dashboard_inteligente.models.random_forest_model import VentasRandomForestModel
import pandas as pd
from datetime import datetime, timedelta

class PrediccionSerializer(serializers.Serializer):
    """Serializer para solicitud de predicción"""
    categoria_id = serializers.IntegerField(required=False)
    meses_a_predecir = serializers.IntegerField(default=1, min_value=1, max_value=12)
    dias_a_predecir = serializers.IntegerField(default=30, min_value=1, max_value=365)

class PrediccionResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de predicción"""
    fecha = serializers.DateField()
    categoria = serializers.CharField()
    prediccion_ventas = serializers.FloatField()
    confianza = serializers.FloatField()

# Vista de API
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class PrediccionesVentaView(APIView):
    """
    API para obtener predicciones de ventas
    """
    
    def post(self, request):
        """
        Genera predicciones de ventas para un período futuro
        """
        serializer = PrediccionSerializer(data=request.data)
        if serializer.is_valid():
            categoria_id = serializer.validated_data.get('categoria_id')
            meses = serializer.validated_data.get('meses_a_predecir', 1)
            
            # Cargar modelo
            modelo = VentasRandomForestModel()
            modelo.cargar()
            
            # Generar fechas futuras
            fechas_futuras = []
            for i in range(1, meses * 30 + 1, 1):
                fecha = datetime.now() + timedelta(days=i)
                # Generar datos de ejemplo para la predicción
                datos_futuros = pd.DataFrame([{
                    'fecha': fecha,
                    'categoria_id': categoria_id or 1,
                    'precio_unitario': 100.0,  # Valor estimado
                }])
                
                prediccion = modelo.predecir(datos_futuros)[0]
                
                fechas_futuras.append({
                    'fecha': fecha.date(),
                    'categoria': f'Categoría {categoria_id or 1}',
                    'prediccion_ventas': float(prediccion),
                    'confianza': 0.85  # Puedes calcular esto con el modelo
                })
            
            return Response(fechas_futuras, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### 2. URLs: Actualizar `dashboard_inteligente/urls.py`

```python
from django.urls import path
from . import views

app_name = 'dashboard_inteligente'

urlpatterns = [
    path('predicciones/', views.PrediccionesVentaView.as_view(), name='predicciones'),
    # path('metricas/', views.MetricasView.as_view(), name='metricas'),
]
```

---

## 📊 Integración con Dashboard

### Endpoint de Métricas Históricas

```python
# En views.py de dashboard_inteligente
from rest_framework.views import APIView
from rest_framework.response import Response
from ventas_carrito.models import Venta
from productos.models import Categoria
from django.db.models import Sum, Count
from datetime import datetime, timedelta

class MetricasHistoricoView(APIView):
    """API para obtener métricas históricas de ventas"""
    
    def get(self, request):
        # Ventas del último mes
        desde = datetime.now() - timedelta(days=30)
        ventas_recientes = Venta.objects.filter(fecha__gte=desde)
        
        # Ventas por categoría
        ventas_por_categoria = Venta.objects.values(
            'producto__categoria__nombre'
        ).annotate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        
        # Ventas por día
        ventas_por_dia = ventas_recientes.values('fecha').annotate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        
        return Response({
            'ventas_por_categoria': list(ventas_por_categoria),
            'ventas_por_dia': list(ventas_por_dia),
            'total_mes_actual': ventas_recientes.aggregate(Sum('total'))['total__sum'] or 0
        })
```

---

## 🎯 Orden de Implementación

1. ✅ Crear estructura de carpetas
2. ✅ Implementar `random_forest_model.py`
3. ✅ Implementar `model_training.py`
4. ✅ Crear serializers y views
5. ✅ Agregar URLs
6. ✅ Generar datos de entrenamiento inicial
7. ✅ Probar entrenamiento del modelo
8. ✅ Implementar API de predicciones
9. ✅ Conectar con frontend (React)

---

## 🔄 Reentrenamiento Automático

Puedes crear una tarea periódica para reentrenar el modelo cada semana:

```python
# dashboard_inteligente/tasks.py
from celery import shared_task
from .models.model_training import entrenar_modelo

@shared_task
def reentrenar_modelo():
    """Tarea periódica para reentrenar el modelo"""
    print("🔄 Iniciando reentrenamiento del modelo...")
    entrenar_modelo()
    print("✅ Reentrenamiento completado")
```

---

## 📝 Notas Importantes

- **Datos mínimos**: Se recomienda al menos 100-200 registros históricos
- **Reentrenamiento**: El modelo se debe reentrenar periódicamente con nuevos datos
- **Validación**: Siempre valida las predicciones con datos de prueba
- **Rendimiento**: Random Forest funciona bien con datasets medianos (< 10000 registros)

---

## 🚀 Comandos Útiles

```bash
# Entrenar modelo desde shell
python manage.py shell
>>> from dashboard_inteligente.models.model_training import entrenar_modelo
>>> modelo = entrenar_modelo()

# Verificar modelo guardado
python manage.py shell
>>> import joblib
>>> from pathlib import Path
>>> model_path = Path('dashboard_inteligente/models/random_forest_model.joblib')
>>> modelo = joblib.load(model_path)
>>> print(modelo)

# Probar predicción
python manage.py shell
>>> from dashboard_inteligente.views import PrediccionesVentaView
>>> # Crear request de prueba
```

---

¡Buena suerte con la implementación! 🎉
