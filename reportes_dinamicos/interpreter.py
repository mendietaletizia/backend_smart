"""
CU14-CU16: Sistema de Interpretación Inteligente de Solicitudes de Reporte
Usa análisis de lenguaje natural mejorado para interpretar solicitudes y generar queries precisas
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter


class ReporteInterpreter:
    """
    Intérprete inteligente de solicitudes de reporte usando NLP mejorado
    Analiza el contexto, intención y entidades para generar reportes precisos
    """
    
    # Patrones de fecha mejorados - EXPANDIDO con más variaciones
    PATRONES_FECHA = {
        'hoy': ['hoy', 'today', 'este día', 'el día de hoy', 'hoy día', 'el día de hoy'],
        'ayer': ['ayer', 'yesterday', 'el día anterior', 'día anterior', 'el día pasado'],
        'semana_pasada': ['última semana', 'semana pasada', 'last week', 'la semana anterior', 
                         'semana anterior', 'la semana pasada', 'semana que pasó'],
        'mes_pasado': ['último mes', 'mes pasado', 'last month', 'el mes anterior', 'mes anterior',
                      'el mes pasado', 'mes que pasó', 'mes anteriormente'],
        'año_pasado': ['último año', 'año pasado', 'last year', 'el año anterior', 'año anterior',
                      'el año pasado', 'año que pasó'],
        'ultimos_dias': ['últimos días', 'last days', 'días pasados', 'días recientes', 'días anteriores',
                        'últimos días', 'días anteriores', 'días previos'],
        'ultima_semana': ['esta semana', 'current week', 'la semana actual', 'semana actual',
                         'semana en curso', 'semana presente'],
        'ultimo_mes': ['este mes', 'current month', 'el mes actual', 'mes actual', 'mes en curso',
                      'mes presente', 'mes corriente'],
        'ultimo_trimestre': ['último trimestre', 'last quarter', 'trimestre pasado', 'trimestre anterior',
                            'el trimestre pasado', 'trimestre que pasó', 'este trimestre', 'trimestre actual'],
        'ultimo_semestre': ['último semestre', 'semestre pasado', 'semestre anterior', 'el semestre pasado',
                           'semestre que pasó', 'este semestre', 'semestre actual'],
        'ultimo_año': ['este año', 'current year', 'el año actual', 'año actual', 'año en curso',
                      'año presente', 'año corriente'],
    }
    
    # Tipos de reporte con sinónimos y contexto - EXPANDIDO para mejor detección
    TIPOS_REPORTE = {
        'ventas': {
            'palabras': ['venta', 'ventas', 'vender', 'vendí', 'vendió', 'vendieron', 'transacciones', 'operaciones', 
                        'comercialización', 'facturación', 'facturas', 'ventas realizadas', 'ventas totales',
                        'cuánto vendí', 'cuanto vendí', 'cuánto se vendió', 'cuanto se vendió', 'ventas del',
                        'ventas de', 'reporte de ventas', 'estadísticas de ventas', 'ventas por'],
            'contexto': ['realizadas', 'totales', 'generadas', 'registradas', 'del mes', 'del año', 'por categoría', 'por producto'],
            'frases': [
                'cuánto vendí', 'cuanto vendí', 'cuánto se vendió', 'cuanto se vendió',
                'ventas del mes', 'ventas del año', 'ventas realizadas', 'ventas totales',
                'reporte de ventas', 'estadísticas de ventas', 'ventas por categoría',
                'ventas por producto', 'ventas por método de pago', 'ventas agrupadas'
            ]
        },
        'mis_compras': {
            'palabras': ['mis compras', 'mis compra', 'compras', 'pedidos', 'mis pedidos', 'mis pedido', 
                        'historial de compras', 'historial compras', 'mis órdenes', 'mis ordenes',
                        'productos que he comprado', 'productos comprados', 'qué he comprado', 'que he comprado',
                        'qué compré', 'que compré', 'compré', 'compraste', 'compró', 'compraron',
                        'pedí', 'pediste', 'pedió', 'ordené', 'ordenaste', 'ordenó', 'mis órdenes',
                        'mis ordenes', 'historial', 'mis adquisiciones', 'lo que compré', 'lo que he comprado',
                        'artículos comprados', 'items comprados', 'productos adquiridos', 'mis adquisiciones',
                        'compras realizadas', 'pedidos realizados', 'órdenes realizadas'],
            'contexto': ['mías', 'propias', 'personales', 'realizadas por mí', 'he comprado', 'compré', 
                        'del último mes', 'del mes', 'del año', 'pendientes', 'completadas'],
            'frases': [
                'mis compras del', 'mis pedidos del', 'historial de compras', 'qué he comprado',
                'qué compré', 'productos que he comprado', 'productos que compré', 'lo que compré',
                'mis compras pendientes', 'mis pedidos pendientes', 'mis compras completadas',
                'historial de mis compras', 'mis compras recientes', 'compras que hice'
            ]
        },
        'productos': {
            'palabras': ['producto', 'productos', 'artículos', 'items', 'mercancía', 'más vendidos', 'mas vendidos', 
                        'más vendido', 'mas vendido', 'top productos', 'productos populares', 'productos destacados',
                        'catálogo', 'catalogo', 'inventario de productos', 'lista de productos', 'productos disponibles',
                        'productos en stock', 'productos con bajo stock', 'productos sin stock', 'productos agotados',
                        'mejores productos', 'productos más populares', 'productos más vendidos', 'top 10 productos',
                        'top productos', 'productos destacados', 'productos recomendados'],
            'contexto': ['catalogo', 'inventario', 'disponibles', 'existentes', 'vendidos', 'populares', 'destacados',
                        'más vendidos', 'con bajo stock', 'sin stock', 'agotados', 'disponibles', 'en stock'],
            'frases': [
                'productos más vendidos', 'productos mas vendidos', 'top productos', 'top 10 productos',
                'productos con bajo stock', 'productos sin stock', 'productos agotados', 'productos disponibles',
                'lista de productos', 'catálogo de productos', 'inventario de productos', 'productos populares',
                'mejores productos', 'productos destacados', 'productos recomendados'
            ]
        },
        'clientes': {
            'palabras': ['cliente', 'clientes', 'usuarios', 'compradores', 'consumidores', 'lista de clientes', 
                        'información de clientes', 'datos de clientes', 'reporte de clientes', 'clientes registrados',
                        'todos los clientes', 'clientes activos', 'clientes frecuentes', 'clientes recurrentes',
                        'clientes más recurrentes', 'clientes vip', 'clientes importantes', 'base de clientes',
                        'clientes del sistema', 'usuarios registrados', 'compradores frecuentes'],
            'contexto': ['registrados', 'activos', 'totales', 'todos', 'listado', 'información', 'datos', 'reporte',
                        'más recurrentes', 'frecuentes', 'vip', 'importantes', 'del sistema'],
            'frases': [
                'lista de clientes', 'todos los clientes', 'clientes registrados', 'clientes activos',
                'clientes más recurrentes', 'clientes frecuentes', 'clientes vip', 'información de clientes',
                'datos de clientes', 'reporte de clientes', 'base de clientes', 'usuarios registrados'
            ]
        },
        'inventario': {
            'palabras': ['inventario', 'stock', 'existencia', 'almacén', 'bodega', 'productos con bajo stock',
                        'productos sin stock', 'productos agotados', 'stock bajo', 'stock mínimo', 'nivel de stock',
                        'control de inventario', 'estado del inventario', 'inventario actual', 'stock disponible'],
            'contexto': ['actual', 'disponible', 'en stock', 'bajo', 'mínimo', 'agotado', 'sin stock', 'control'],
            'frases': [
                'productos con bajo stock', 'productos sin stock', 'productos agotados', 'stock bajo',
                'inventario actual', 'estado del inventario', 'control de inventario', 'stock disponible',
                'nivel de stock', 'productos con stock mínimo'
            ]
        },
        'financiero': {
            'palabras': ['financiero', 'dinero', 'ingresos', 'ganancias', 'pérdidas', 'balance', 
                        'finanzas', 'economía', 'revenue', 'revenues', 'gasto', 'gastos', 'gasté', 
                        'gastado', 'cuánto', 'cuanto', 'cuánta', 'cuanta', 'he gastado', 'he gasto',
                        'total gastado', 'monto', 'montos', 'inversión', 'inversiones', 'resumen de mis gastos',
                        'resumen gastos', 'mis gastos', 'gastos totales', 'cuánto gasté', 'cuanto gasté',
                        'cuánto he gastado', 'cuanto he gastado', 'cuánto dinero', 'cuanto dinero',
                        'resumen financiero', 'estado financiero', 'balance financiero', 'ingresos totales',
                        'ganancias totales', 'pérdidas totales', 'flujo de caja', 'ingresos del mes',
                        'ingresos del año', 'ingresos del trimestre', 'ingresos del semestre',
                        'entró', 'entró de', 'entró en', 'ingresó', 'ingresó de', 'ingresó en',
                        'me entró', 'me ingresó', 'cuánto me entró', 'cuanto me entró', 'cuánta me entró',
                        'cuanta me entró', 'cuánto dinero me entró', 'cuanto dinero me entró',
                        'cuánta dinero me entró', 'cuanta dinero me entró', 'dinero que entró',
                        'dinero que ingresó', 'cuánto entró de ventas', 'cuanto entró de ventas'],
            'contexto': ['resumen', 'análisis', 'estado', 'situación', 'total', 'suma', 'de mis', 'personales',
                        'del mes', 'del año', 'del trimestre', 'del semestre', 'totales', 'de ventas',
                        'por ventas', 'en ventas', 'de las ventas'],
            'frases': [
                'cuánto he gastado', 'cuanto he gastado', 'cuánto gasté', 'cuanto gasté', 'cuánto dinero',
                'resumen de mis gastos', 'mis gastos', 'gastos totales', 'total gastado', 'resumen financiero',
                'ingresos del mes', 'ingresos del año', 'ingresos del trimestre', 'ingresos del semestre',
                'ingresos totales', 'ganancias totales', 'balance financiero', 'estado financiero',
                'cuánto dinero me entró', 'cuanto dinero me entró', 'cuánta dinero me entró', 'cuanta dinero me entró',
                'cuánto me entró de ventas', 'cuanto me entró de ventas', 'cuánta dinero me entro de ventas',
                'cuanta dinero me entro de ventas', 'cuánto ingresó de ventas', 'cuanto ingresó de ventas',
                'dinero que entró de ventas', 'dinero que ingresó de ventas', 'ingresos de ventas',
                'cuánto entró', 'cuanto entró', 'cuánta entró', 'cuanta entró'
            ]
        },
    }
    
    # Métricas con sinónimos
    METRICAS = {
        'total': ['total', 'suma', 'sumar', 'totalizar', 'sumatoria', 'sumatorio', 'suma total'],
        'promedio': ['promedio', 'media', 'promediar', 'media aritmética', 'promedio aritmético'],
        'cantidad': ['cantidad', 'número', 'contar', 'cuántos', 'cuántas', 'count', 'número de'],
        'maximo': ['máximo', 'max', 'mayor', 'más alto', 'peak', 'pico', 'top'],
        'minimo': ['mínimo', 'min', 'menor', 'más bajo', 'lowest', 'bottom'],
        'mediana': ['mediana', 'median', 'valor medio'],
    }
    
    # Filtros con sinónimos
    FILTROS = {
        'categoria': ['categoría', 'categoria', 'tipo', 'clase', 'rubro', 'grupo'],
        'fecha': ['fecha', 'día', 'mes', 'año', 'período', 'periodo', 'rango', 'intervalo'],
        'producto': ['producto', 'artículo', 'item', 'mercancía'],
        'cliente': ['cliente', 'comprador', 'usuario', 'consumidor'],
        'estado': ['estado', 'status', 'situación', 'condición'],
        'metodo_pago': ['método de pago', 'metodo de pago', 'pago', 'forma de pago', 'tipo de pago'],
    }
    
    # Palabras de agrupación
    AGRUPACION_KEYWORDS = {
        'dia': ['por día', 'diario', 'día a día', 'daily', 'por día'],
        'semana': ['por semana', 'semanal', 'semana a semana', 'weekly'],
        'mes': ['por mes', 'mensual', 'mes a mes', 'monthly'],
        'año': ['por año', 'anual', 'año a año', 'yearly', 'anual'],
        'categoria': ['por categoría', 'por categoria', 'agrupado por categoría', 'grouped by category'],
        'producto': ['por producto', 'agrupado por producto', 'grouped by product'],
        'cliente': ['por cliente', 'agrupado por cliente', 'grouped by client'],
    }
    
    def interpretar(self, texto: str) -> Dict[str, Any]:
        """
        Interpreta una solicitud de reporte usando análisis inteligente de lenguaje natural
        
        Args:
            texto: Texto de la solicitud en lenguaje natural
            
        Returns:
            Diccionario con parámetros interpretados de forma inteligente
        """
        texto_original = texto.strip()
        texto_lower = texto_original.lower()
        
        # Análisis de intención y contexto
        intencion = self._analizar_intencion(texto_lower)
        
        # Extracción de entidades
        tipo_reporte = self._detectar_tipo_reporte_inteligente(texto_lower, intencion)
        metricas = self._detectar_metricas_inteligentes(texto_lower)
        filtros = self._detectar_filtros_inteligentes(texto_lower, texto_original)
        fechas = self._detectar_fechas_inteligentes(texto_lower)
        agrupacion = self._detectar_agrupacion_inteligente(texto_lower)
        formato = self._detectar_formato_inteligente(texto_lower)
        
        # Análisis de contexto adicional
        contexto = self._analizar_contexto(texto_lower)
        
        resultado = {
            'tipo_reporte': tipo_reporte,
            'metricas': metricas,
            'filtros': filtros,
            'fechas': fechas,
            'agrupacion': agrupacion,
            'formato': formato,
            'texto_original': texto_original,
            'texto_lower': texto_lower,  # Agregar también la versión en minúsculas para búsquedas
            'intencion': intencion,
            'contexto': contexto,
            'confianza': self._calcular_confianza(texto_lower, tipo_reporte, fechas)
        }
        
        return resultado
    
    def _analizar_intencion(self, texto: str) -> str:
        """Analiza la intención principal de la solicitud - MEJORADO con más variaciones"""
        intenciones = {
            'consultar': [
                'mostrar', 'ver', 'consultar', 'obtener', 'listar', 'ver lista', 'quiero ver',
                'dame', 'muéstrame', 'necesito ver', 'quiero saber', 'dame información',
                'muéstrame información', 'quiero información', 'necesito información',
                'dame un reporte', 'muéstrame un reporte', 'quiero un reporte', 'necesito un reporte',
                'dame la lista', 'muéstrame la lista', 'quiero la lista', 'necesito la lista',
                'dame los datos', 'muéstrame los datos', 'quiero los datos', 'necesito los datos',
                'cuál', 'cual', 'qué', 'que', 'cuáles', 'cuales', 'dónde', 'donde'
            ],
            'analizar': [
                'analizar', 'análisis', 'estadísticas', 'estadisticas', 'métricas', 'metricas',
                'analiza', 'haz un análisis', 'necesito un análisis', 'quiero un análisis',
                'estadística', 'estadisticas', 'métricas', 'metricas', 'indicadores'
            ],
            'comparar': [
                'comparar', 'comparación', 'vs', 'versus', 'diferencias', 'comparar',
                'comparar con', 'comparación entre', 'diferencias entre', 'comparar entre'
            ],
            'resumir': [
                'resumen', 'resumir', 'sumario', 'total', 'totales', 'resumen de',
                'dame un resumen', 'muéstrame un resumen', 'quiero un resumen', 'necesito un resumen',
                'resumen total', 'resumen general', 'resumen completo'
            ],
        }
        
        texto_lower = texto.lower()
        
        for intencion, palabras in intenciones.items():
            for palabra in palabras:
                if palabra in texto_lower:
                    return intencion
        
        return 'consultar'  # Por defecto
    
    def _detectar_tipo_reporte_inteligente(self, texto: str, intencion: str) -> str:
        """
        Detecta el tipo de reporte usando análisis de contexto y similitud mejorado
        Ahora con detección de frases completas y mejor análisis de contexto
        """
        texto_lower = texto.lower().strip()
        texto_original = texto.lower()
        scores = {}
        
        # PRIMERO: Buscar frases completas (máxima prioridad)
        for tipo, info in self.TIPOS_REPORTE.items():
            frases = info.get('frases', [])
            for frase in frases:
                if frase in texto_lower:
                    # Si es una frase completa, darle máxima prioridad
                    if tipo == 'mis_compras' or tipo == 'financiero':
                        # Verificar si hay indicadores personales para confirmar
                        indicadores_personales = ['mis', 'mi', 'he', 'compré', 'gasté', 'pedí', 'ordené']
                        if any(ind in texto_lower for ind in indicadores_personales) or tipo == 'financiero':
                            return tipo
                    else:
                        return tipo
        
        # SEGUNDO: Expandir sinónimos y variaciones comunes
        texto_expandido = texto_lower
        sinónimos_expansion = {
            'compré': 'compras',
            'compraste': 'compras',
            'compró': 'compras',
            'compraron': 'compras',
            'pedí': 'pedidos',
            'ordené': 'ordenes',
            'gasté': 'gastos',
            'gastaste': 'gastos',
            'gastó': 'gastos',
            'vendí': 'ventas',
            'vendió': 'ventas',
            'vendieron': 'ventas',
        }
        for sinónimo, palabra_base in sinónimos_expansion.items():
            if sinónimo in texto_lower:
                texto_expandido += ' ' + palabra_base
        
        # TERCERO: Priorizar "mis compras" si hay indicadores de primera persona
        indicadores_personales = [
            'mis', 'mi', 'mío', 'mía', 'mías', 'propias', 'personales', 
            'yo', 'me', 'he', 'he gastado', 'he comprado', 'he pedido',
            'compré', 'gasté', 'pedí', 'ordené', 'quiero ver mis',
            'quiero ver mi', 'dame mis', 'muéstrame mis', 'muéstrame mi',
            'necesito ver mis', 'quiero saber mis', 'dame información de mis'
        ]
        es_personal = any(ind in texto_lower for ind in indicadores_personales)
        
        if es_personal:
            # Verificar si hay palabras relacionadas con compras o gastos
            palabras_compras = [
                'compra', 'compras', 'compré', 'compraste', 'compró',
                'pedido', 'pedidos', 'pedí', 'orden', 'ordenes', 'ordené',
                'historial', 'historiales', 'gasto', 'gastos', 'gasté', 
                'gastado', 'cuánto', 'cuanto', 'cuánta', 'cuanta',
                'qué compré', 'que compré', 'qué he comprado', 'que he comprado',
                'lo que compré', 'lo que he comprado', 'productos que compré'
            ]
            if any(palabra in texto_lower for palabra in palabras_compras):
                # Si menciona gastos o dinero, puede ser financiero pero de sus compras
                palabras_financieras = [
                    'gasto', 'gastos', 'gasté', 'gastado', 'dinero', 
                    'cuánto', 'cuanto', 'monto', 'total', 'resumen',
                    'cuánto he gastado', 'cuanto he gastado', 'cuánto gasté',
                    'cuanto gasté', 'total gastado', 'gastos totales',
                    'resumen de mis gastos', 'resumen gastos'
                ]
                if any(palabra in texto_lower for palabra in palabras_financieras):
                    return 'financiero'  # Se convertirá a mis_compras con enfoque financiero
                
                # Si menciona "productos que he comprado" o similar
                if any(frase in texto_lower for frase in [
                    'productos que he comprado', 'productos comprados',
                    'qué he comprado', 'que he comprado', 'qué compré',
                    'que compré', 'lista de productos', 'productos que compré',
                    'lo que compré', 'lo que he comprado', 'artículos comprados'
                ]):
                    return 'mis_compras'  # Se detectará como lista de productos
                
                return 'mis_compras'
        
        # CUARTO: Calcular score para cada tipo de reporte con matching mejorado
        for tipo, info in self.TIPOS_REPORTE.items():
            score = 0
            palabras = info.get('palabras', [])
            contexto = info.get('contexto', [])
            frases = info.get('frases', [])
            
            # Matching de frases completas (peso muy alto)
            for frase in frases:
                if frase in texto_lower:
                    score += 5  # Peso muy alto para frases completas
            
            # Matching exacto de palabras clave (peso alto)
            for palabra in palabras:
                if palabra in texto_lower:
                    # Peso mayor si la palabra está al inicio o es más específica
                    if texto_lower.startswith(palabra) or len(palabra) > 5:
                        score += 3
                    else:
                        score += 2
            
            # Matching parcial (peso medio) - para capturar variaciones
            palabras_texto = set(texto_lower.split())
            for palabra in palabras:
                # Buscar palabras que contengan la palabra clave o viceversa
                for palabra_texto in palabras_texto:
                    if len(palabra) > 3 and len(palabra_texto) > 3:
                        if palabra in palabra_texto or palabra_texto in palabra:
                            score += 1
            
            # Contar coincidencias de contexto
            for ctx in contexto:
                if ctx in texto_lower:
                    score += 1
            
            # Bonus por frases completas comunes
            frases_comunes = [
                f'reporte de {tipo}',
                f'{tipo} del',
                f'{tipo} de',
                f'lista de {tipo}',
                f'información de {tipo}',
                f'dame {tipo}',
                f'muéstrame {tipo}',
                f'quiero ver {tipo}',
                f'necesito {tipo}'
            ]
            for frase in frases_comunes:
                if frase in texto_lower:
                    score += 2
            
            scores[tipo] = score
        
        # QUINTO: Si hay un score claro, retornarlo
        if scores:
            tipo_max = max(scores, key=scores.get)
            score_max = scores[tipo_max]
            
            # Si el score es suficientemente alto, retornar ese tipo
            if score_max >= 2:
                return tipo_max
            
            # Si hay empate o scores bajos, usar heurísticas adicionales
            if score_max > 0:
                # Verificar si hay palabras específicas que indiquen el tipo
                palabras_especificas = {
                    'ventas': ['transacción', 'transacciones', 'operación', 'operaciones', 'vender', 'facturación'],
                    'productos': ['artículo', 'artículos', 'item', 'items', 'mercancía', 'catálogo', 'catalogo'],
                    'clientes': ['usuario', 'usuarios', 'comprador', 'compradores', 'consumidor'],
                    'inventario': ['stock', 'existencia', 'almacén', 'bodega', 'disponible'],
                    'financiero': ['ingreso', 'ingresos', 'ganancia', 'ganancias', 'balance', 'finanzas', 'revenue']
                }
                
                for tipo_check, palabras_check in palabras_especificas.items():
                    if any(palabra in texto_lower for palabra in palabras_check):
                        if tipo_check in scores and scores[tipo_check] > 0:
                            return tipo_check
                
                return tipo_max
        
        # SEXTO: Fallback - intentar inferir del contexto general con más variaciones
        palabras_consulta = ['ver', 'mostrar', 'listar', 'obtener', 'dame', 'quiero', 'necesito', 
                            'muéstrame', 'dame información', 'quiero saber', 'necesito ver',
                            'quiero ver', 'dame un reporte', 'muéstrame un reporte', 'quiero un reporte']
        
        if any(palabra in texto_lower for palabra in palabras_consulta):
            # Si es una solicitud general sin tipo específico, intentar inferir
            if any(palabra in texto_lower for palabra in ['compra', 'pedido', 'orden', 'historial']):
                return 'mis_compras'
            elif any(palabra in texto_lower for palabra in ['venta', 'transacción', 'factura']):
                return 'ventas'
            elif any(palabra in texto_lower for palabra in ['producto', 'artículo', 'item', 'catálogo']):
                return 'productos'
            elif any(palabra in texto_lower for palabra in ['cliente', 'usuario', 'comprador']):
                return 'clientes'
            elif any(palabra in texto_lower for palabra in ['stock', 'inventario', 'almacén']):
                return 'inventario'
            elif any(palabra in texto_lower for palabra in ['dinero', 'gasto', 'ingreso', 'financiero']):
                return 'financiero'
        
        return 'general'
    
    def _detectar_metricas_inteligentes(self, texto: str) -> List[str]:
        """Detecta métricas solicitadas con análisis de contexto"""
        metricas = []
        texto_lower = texto.lower()
        
        for metrica, palabras in self.METRICAS.items():
            for palabra in palabras:
                if palabra in texto_lower:
                    # Verificar contexto para evitar falsos positivos
                    if self._verificar_contexto_metrica(texto_lower, palabra, metrica):
                        metricas.append(metrica)
                        break
        
        # Si no se detectó ninguna, usar 'total' por defecto
        if not metricas:
            metricas = ['total']
        
        return list(set(metricas))  # Eliminar duplicados
    
    def _verificar_contexto_metrica(self, texto: str, palabra: str, metrica: str) -> bool:
        """Verifica que la palabra esté en el contexto correcto"""
        # Buscar la palabra y verificar que esté cerca de palabras relacionadas con reportes
        palabras_reporte = ['reporte', 'mostrar', 'ver', 'obtener', 'calcular', 'total', 'suma']
        indice = texto.find(palabra)
        
        if indice != -1:
            # Verificar contexto cercano (50 caracteres antes y después)
            contexto = texto[max(0, indice-50):indice+50]
            return any(pr in contexto for pr in palabras_reporte)
        
        return True
    
    def _detectar_filtros_inteligentes(self, texto: str, texto_original: str) -> Dict[str, Any]:
        """Detecta filtros con extracción de entidades mejorada y más flexible"""
        filtros = {}
        texto_lower = texto.lower()
        
        # Filtrar por categoría (mejorado con más patrones)
        patrones_categoria = [
            r'categor[íi]a[:\s]+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.|del|de la)',
            r'de\s+la\s+categor[íi]a\s+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.)',
            r'en\s+categor[íi]a\s+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.)',
            r'categor[íi]a\s+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.)',
            r'tipo\s+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.)',
        ]
        for patron in patrones_categoria:
            match = re.search(patron, texto_lower, re.IGNORECASE)
            if match:
                categoria_nombre = match.group(1).strip()
                # Limpiar palabras comunes y caracteres especiales
                categoria_nombre = re.sub(r'\b(de|la|el|las|los|un|una|del|de la|en|por)\b', '', categoria_nombre, flags=re.IGNORECASE).strip()
                categoria_nombre = re.sub(r'[^\w\s\-]', '', categoria_nombre).strip()
                if categoria_nombre and len(categoria_nombre) > 1:
                    filtros['categoria'] = categoria_nombre
                    break
        
        # Filtrar por estado (mejorado)
        estados_map = {
            'completada': ['completada', 'completadas', 'finalizada', 'finalizadas', 'terminada', 'terminadas', 'completado', 'completados'],
            'pendiente': ['pendiente', 'pendientes', 'en proceso', 'procesando', 'en espera', 'esperando', 'por procesar', 'sin completar'],
            'cancelada': ['cancelada', 'canceladas', 'anulada', 'anuladas', 'rechazada', 'rechazadas', 'cancelado', 'cancelados'],
        }
        for estado, palabras in estados_map.items():
            if any(palabra in texto_lower for palabra in palabras):
                filtros['estado'] = estado
                break
        
        # Detección especial para frases comunes como "mis compras pendientes"
        if 'compras' in texto_lower or 'compra' in texto_lower or 'pedidos' in texto_lower or 'pedido' in texto_lower:
            if any(palabra in texto_lower for palabra in ['pendiente', 'pendientes', 'en proceso', 'procesando', 'en espera']):
                filtros['estado'] = 'pendiente'
            elif any(palabra in texto_lower for palabra in ['completada', 'completadas', 'finalizada', 'terminada']):
                filtros['estado'] = 'completada'
        
        # Filtrar por método de pago - Solo Stripe
        metodos_pago_map = {
            'stripe': ['stripe', 'online', 'pago online', 'pago en línea', 'pago en linea'],
        }
        for metodo, palabras in metodos_pago_map.items():
            if any(palabra in texto_lower for palabra in palabras):
                filtros['metodo_pago'] = metodo
                break
        
        # Filtrar por producto específico (mejorado)
        patrones_producto = [
            r'producto[:\s]+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.|del|de la)',
            r'el\s+producto\s+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.)',
            r'artículo[:\s]+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.)',
        ]
        for patron in patrones_producto:
            match = re.search(patron, texto_lower, re.IGNORECASE)
            if match:
                producto_nombre = match.group(1).strip()
                producto_nombre = re.sub(r'\b(de|la|el|las|los|un|una|del|de la)\b', '', producto_nombre, flags=re.IGNORECASE).strip()
                if producto_nombre and len(producto_nombre) > 2:
                    filtros['producto'] = producto_nombre
                    break
        
        # Filtrar por nombre de cliente (para administradores)
        patrones_cliente = [
            r'cliente[:\s]+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.)',
            r'del\s+cliente\s+([a-záéíóúñ0-9\s\-]+?)(?:\s|$|,|\.)',
        ]
        for patron in patrones_cliente:
            match = re.search(patron, texto_lower, re.IGNORECASE)
            if match:
                cliente_nombre = match.group(1).strip()
                cliente_nombre = re.sub(r'\b(de|la|el|las|los|un|una|del|de la)\b', '', cliente_nombre, flags=re.IGNORECASE).strip()
                if cliente_nombre and len(cliente_nombre) > 2:
                    filtros['cliente'] = cliente_nombre
                    break
        
        return filtros
    
    def _detectar_fechas_inteligentes(self, texto: str) -> Dict[str, Any]:
        """Detecta fechas con análisis mejorado de expresiones temporales"""
        fechas = {}
        texto_lower = texto.lower()
        hoy = datetime.now().date()
        
        # Detectar expresiones temporales comunes
        if any(palabra in texto_lower for palabra in self.PATRONES_FECHA['hoy']):
            fechas['desde'] = hoy.isoformat()
            fechas['hasta'] = hoy.isoformat()
        elif any(palabra in texto_lower for palabra in self.PATRONES_FECHA['ayer']):
            fecha_ayer = hoy - timedelta(days=1)
            fechas['desde'] = fecha_ayer.isoformat()
            fechas['hasta'] = fecha_ayer.isoformat()
        elif any(palabra in texto_lower for palabra in self.PATRONES_FECHA['ultima_semana']):
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            fechas['desde'] = inicio_semana.isoformat()
            fechas['hasta'] = hoy.isoformat()
        elif any(palabra in texto_lower for palabra in self.PATRONES_FECHA['semana_pasada']):
            inicio_semana_pasada = hoy - timedelta(days=hoy.weekday() + 7)
            fin_semana_pasada = inicio_semana_pasada + timedelta(days=6)
            fechas['desde'] = inicio_semana_pasada.isoformat()
            fechas['hasta'] = fin_semana_pasada.isoformat()
        elif any(palabra in texto_lower for palabra in self.PATRONES_FECHA['ultimo_mes']):
            primer_dia_mes = hoy.replace(day=1)
            fechas['desde'] = primer_dia_mes.isoformat()
            fechas['hasta'] = hoy.isoformat()
        elif any(palabra in texto_lower for palabra in self.PATRONES_FECHA['mes_pasado']):
            primer_dia_mes_pasado = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1)
            ultimo_dia_mes_pasado = hoy.replace(day=1) - timedelta(days=1)
            fechas['desde'] = primer_dia_mes_pasado.isoformat()
            fechas['hasta'] = ultimo_dia_mes_pasado.isoformat()
        elif any(palabra in texto_lower for palabra in self.PATRONES_FECHA['ultimo_trimestre']):
            mes_actual = hoy.month
            trimestre_actual = (mes_actual - 1) // 3
            primer_mes_trimestre = trimestre_actual * 3 + 1
            primer_dia_trimestre = hoy.replace(month=primer_mes_trimestre, day=1)
            fechas['desde'] = primer_dia_trimestre.isoformat()
            fechas['hasta'] = hoy.isoformat()
        elif any(palabra in texto_lower for palabra in self.PATRONES_FECHA['ultimo_semestre']):
            mes_actual = hoy.month
            semestre_actual = 1 if mes_actual <= 6 else 2
            primer_mes_semestre = 1 if semestre_actual == 1 else 7
            primer_dia_semestre = hoy.replace(month=primer_mes_semestre, day=1)
            fechas['desde'] = primer_dia_semestre.isoformat()
            fechas['hasta'] = hoy.isoformat()
        elif any(palabra in texto_lower for palabra in self.PATRONES_FECHA['año_pasado']):
            fechas['desde'] = hoy.replace(year=hoy.year - 1, month=1, day=1).isoformat()
            fechas['hasta'] = hoy.replace(year=hoy.year - 1, month=12, day=31).isoformat()
        elif any(palabra in texto_lower for palabra in self.PATRONES_FECHA['ultimo_año']):
            fechas['desde'] = hoy.replace(month=1, day=1).isoformat()
            fechas['hasta'] = hoy.isoformat()
        elif 'últimos' in texto_lower or 'last' in texto_lower:
            # Detectar "últimos N días/semanas/meses/trimestres/semestres"
            match = re.search(r'últimos?\s+(\d+)\s+(día|días|semana|semanas|mes|meses|trimestre|trimestres|semestre|semestres)', texto_lower)
            if match:
                cantidad = int(match.group(1))
                unidad = match.group(2)
                if 'día' in unidad:
                    fechas['desde'] = (hoy - timedelta(days=cantidad)).isoformat()
                    fechas['hasta'] = hoy.isoformat()
                elif 'semana' in unidad:
                    fechas['desde'] = (hoy - timedelta(weeks=cantidad)).isoformat()
                    fechas['hasta'] = hoy.isoformat()
                elif 'mes' in unidad:
                    # Aproximar meses a días
                    fechas['desde'] = (hoy - timedelta(days=cantidad * 30)).isoformat()
                    fechas['hasta'] = hoy.isoformat()
                elif 'trimestre' in unidad:
                    # Aproximar trimestres a días (3 meses = 90 días)
                    fechas['desde'] = (hoy - timedelta(days=cantidad * 90)).isoformat()
                    fechas['hasta'] = hoy.isoformat()
                elif 'semestre' in unidad:
                    # Aproximar semestres a días (6 meses = 180 días)
                    fechas['desde'] = (hoy - timedelta(days=cantidad * 180)).isoformat()
                    fechas['hasta'] = hoy.isoformat()
        
        # Detectar fechas específicas (DD/MM/YYYY o YYYY-MM-DD)
        fecha_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', texto_lower)
        if fecha_match:
            dia, mes, anio = map(int, fecha_match.groups())
            try:
                fecha = datetime(anio, mes, dia).date()
                fechas['desde'] = fecha.isoformat()
                fechas['hasta'] = fecha.isoformat()
            except:
                pass
        
        # Detectar rango de fechas
        rango_match = re.search(
            r'(?:desde|from)\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})\s+(?:hasta|to)\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            texto_lower
        )
        if rango_match:
            dia1, mes1, anio1, dia2, mes2, anio2 = map(int, rango_match.groups())
            try:
                fechas['desde'] = datetime(anio1, mes1, dia1).date().isoformat()
                fechas['hasta'] = datetime(anio2, mes2, dia2).date().isoformat()
            except:
                pass
        
        return fechas
    
    def _detectar_agrupacion_inteligente(self, texto: str) -> List[str]:
        """Detecta agrupación solicitada con análisis de contexto"""
        agrupacion = []
        texto_lower = texto.lower()
        
        # Detectar "más vendidos" o "mas vendidos" como indicador de ordenamiento por ventas
        if any(frase in texto_lower for frase in ['más vendidos', 'mas vendidos', 'más vendido', 'mas vendido', 'top productos', 'productos populares']):
            agrupacion.append('ventas')
        
        for tipo, keywords in self.AGRUPACION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in texto_lower:
                    agrupacion.append(tipo)
                    break
        
        return list(set(agrupacion))  # Eliminar duplicados
    
    def _detectar_formato_inteligente(self, texto: str) -> str:
        """Detecta el formato deseado del reporte"""
        texto_lower = texto.lower()
        
        if any(palabra in texto_lower for palabra in ['pdf', 'documento pdf', 'archivo pdf']):
            return 'pdf'
        elif any(palabra in texto_lower for palabra in ['excel', 'xlsx', 'hoja de cálculo', 'spreadsheet']):
            return 'excel'
        elif any(palabra in texto_lower for palabra in ['json', 'datos json', 'formato json']):
            return 'json'
        elif any(palabra in texto_lower for palabra in ['pantalla', 'ver', 'mostrar', 'visualizar', 'display']):
            return 'pantalla'
        
        return 'pantalla'  # Por defecto
    
    def _analizar_contexto(self, texto: str) -> Dict[str, Any]:
        """Analiza el contexto adicional de la solicitud"""
        contexto = {
            'es_pregunta': '?' in texto or any(palabra in texto for palabra in ['cuánto', 'cuánta', 'cuántos', 'cuántas', 'qué', 'cuál']),
            'es_comparacion': any(palabra in texto for palabra in ['comparar', 'vs', 'versus', 'diferencias', 'comparación']),
            'es_tendencia': any(palabra in texto for palabra in ['tendencia', 'evolución', 'crecimiento', 'decrecimiento', 'tendencies']),
            'nivel_detalle': 'detallado' if any(palabra in texto for palabra in ['detallado', 'detalle', 'completo', 'extenso']) else 'resumen'
        }
        return contexto
    
    def _calcular_confianza(self, texto: str, tipo_reporte: str, fechas: Dict) -> float:
        """
        Calcula un score de confianza en la interpretación (0.0 a 1.0)
        """
        confianza = 0.4  # Base más conservadora
        
        # Aumentar confianza si se detectó tipo de reporte específico
        if tipo_reporte != 'general':
            confianza += 0.25
            # Bonus si el tipo es muy específico
            if tipo_reporte in ['mis_compras', 'financiero']:
                confianza += 0.1
        
        # Aumentar confianza si se detectaron fechas
        if fechas:
            confianza += 0.15
        
        # Aumentar confianza si el texto tiene suficiente contexto
        if len(texto) > 15:
            confianza += 0.1
        if len(texto) > 30:
            confianza += 0.05
        
        # Penalizar si el texto es muy corto o ambiguo
        if len(texto) < 5:
            confianza -= 0.2
        
        return max(0.3, min(confianza, 1.0))  # Mínimo 0.3, máximo 1.0
    
    def procesar_audio(self, audio_data: bytes) -> str:
        """
        Procesa audio y convierte a texto
        Por ahora, retorna texto simulado
        En producción, usar servicios como Google Speech-to-Text o Azure Speech
        """
        # TODO: Implementar conversión de audio a texto real
        # Por ahora, retornar texto simulado
        return "Reporte de ventas del último mes"


def interpretar_voz(audio_data: bytes, interpreter: ReporteInterpreter) -> Dict[str, Any]:
    """
    Función auxiliar para procesar solicitud por voz
    
    Args:
        audio_data: Datos de audio
        interpreter: Instancia de ReporteInterpreter
        
    Returns:
        Parámetros interpretados
    """
    texto = interpreter.procesar_audio(audio_data)
    return interpreter.interpretar(texto)
