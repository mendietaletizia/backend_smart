"""
CU14-CU16: Sistema de Interpretación de Solicitudes de Reporte
Interpreta solicitudes en texto o voz y genera queries para reportes
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class ReporteInterpreter:
    """
    Interprete de solicitudes de reporte usando NLP básico (regex + keywords)
    """
    
    # Patrones de fecha
    PATRONES_FECHA = {
        r'hoy|today': 'hoy',
        r'ayer|yesterday': 'ayer',
        r'última semana|last week|semana pasada': 'semana_pasada',
        r'último mes|last month|mes pasado': 'mes_pasado',
        r'último año|last year|año pasado': 'año_pasado',
        r'(\d{1,2})/(\d{1,2})/(\d{4})': 'fecha_especifica',  # DD/MM/YYYY
        r'(\d{4})-(\d{1,2})-(\d{1,2})': 'fecha_especifica',  # YYYY-MM-DD
    }
    
    # Palabras clave para tipos de reporte
    TIPOS_REPORTE = {
        'ventas': ['venta', 'ventas', 'vender', 'compras', 'transacciones'],
        'productos': ['producto', 'productos', 'inventario', 'stock', 'artículos'],
        'clientes': ['cliente', 'clientes', 'usuarios', 'compradores'],
        'inventario': ['inventario', 'stock', 'existencia', 'almacén'],
        'financiero': ['financiero', 'dinero', 'ingresos', 'ganancias', 'pérdidas', 'balance'],
    }
    
    # Palabras clave para métricas
    METRICAS = {
        'total': ['total', 'suma', 'sumar', 'totalizar'],
        'promedio': ['promedio', 'media', 'promediar'],
        'cantidad': ['cantidad', 'número', 'contar', 'cuántos'],
        'maximo': ['máximo', 'max', 'mayor', 'más alto'],
        'minimo': ['mínimo', 'min', 'menor', 'más bajo'],
    }
    
    # Palabras clave para filtros
    FILTROS = {
        'categoria': ['categoría', 'categoria', 'tipo', 'clase'],
        'fecha': ['fecha', 'día', 'mes', 'año', 'período', 'periodo'],
        'producto': ['producto', 'artículo', 'item'],
        'cliente': ['cliente', 'comprador', 'usuario'],
        'estado': ['estado', 'status', 'situación'],
    }
    
    def interpretar(self, texto: str) -> Dict[str, Any]:
        """
        Interpreta una solicitud de reporte y retorna parámetros estructurados
        
        Args:
            texto: Texto de la solicitud
            
        Returns:
            Diccionario con parámetros interpretados
        """
        texto_lower = texto.lower().strip()
        
        resultado = {
            'tipo_reporte': self._detectar_tipo_reporte(texto_lower),
            'metricas': self._detectar_metricas(texto_lower),
            'filtros': self._detectar_filtros(texto_lower),
            'fechas': self._detectar_fechas(texto_lower),
            'agrupacion': self._detectar_agrupacion(texto_lower),
            'formato': self._detectar_formato(texto_lower),
            'texto_original': texto
        }
        
        return resultado
    
    def _detectar_tipo_reporte(self, texto: str) -> str:
        """Detecta el tipo de reporte solicitado"""
        for tipo, palabras in self.TIPOS_REPORTE.items():
            for palabra in palabras:
                if palabra in texto:
                    return tipo
        return 'general'
    
    def _detectar_metricas(self, texto: str) -> List[str]:
        """Detecta métricas solicitadas"""
        metricas = []
        for metrica, palabras in self.METRICAS.items():
            for palabra in palabras:
                if palabra in texto:
                    metricas.append(metrica)
                    break
        return metricas if metricas else ['total']  # Por defecto, total
    
    def _detectar_filtros(self, texto: str) -> Dict[str, Any]:
        """Detecta filtros en la solicitud"""
        filtros = {}
        
        # Filtrar por categoría
        categoria_match = re.search(r'categor[íi]a[:\s]+([a-záéíóúñ\s]+)', texto, re.IGNORECASE)
        if categoria_match:
            categoria_nombre = categoria_match.group(1).strip()
            filtros['categoria'] = categoria_nombre
        
        # Filtrar por estado
        if 'completada' in texto or 'completadas' in texto:
            filtros['estado'] = 'completada'
        elif 'pendiente' in texto or 'pendientes' in texto:
            filtros['estado'] = 'pendiente'
        elif 'cancelada' in texto or 'canceladas' in texto:
            filtros['estado'] = 'cancelada'
        
        # Filtrar por método de pago
        if 'tarjeta' in texto or 'tarjeta' in texto:
            filtros['metodo_pago'] = 'tarjeta_credito'
        elif 'efectivo' in texto:
            filtros['metodo_pago'] = 'efectivo'
        elif 'transferencia' in texto:
            filtros['metodo_pago'] = 'transferencia'
        
        return filtros
    
    def _detectar_fechas(self, texto: str) -> Dict[str, Any]:
        """Detecta fechas en la solicitud y retorna strings ISO para JSON"""
        fechas = {}
        
        # Detectar fechas relativas
        if 'hoy' in texto or 'today' in texto:
            fecha_hoy = datetime.now().date()
            fechas['desde'] = fecha_hoy.isoformat()
            fechas['hasta'] = fecha_hoy.isoformat()
        elif 'ayer' in texto or 'yesterday' in texto:
            fecha_ayer = datetime.now().date() - timedelta(days=1)
            fechas['desde'] = fecha_ayer.isoformat()
            fechas['hasta'] = fecha_ayer.isoformat()
        elif 'semana pasada' in texto or 'última semana' in texto or 'last week' in texto:
            hoy = datetime.now().date()
            inicio_semana = hoy - timedelta(days=hoy.weekday() + 7)
            fin_semana = inicio_semana + timedelta(days=6)
            fechas['desde'] = inicio_semana.isoformat()
            fechas['hasta'] = fin_semana.isoformat()
        elif 'mes pasado' in texto or 'último mes' in texto or 'last month' in texto:
            hoy = datetime.now().date()
            primer_dia_mes_pasado = hoy.replace(day=1) - timedelta(days=1)
            primer_dia_mes_pasado = primer_dia_mes_pasado.replace(day=1)
            ultimo_dia_mes_pasado = hoy.replace(day=1) - timedelta(days=1)
            fechas['desde'] = primer_dia_mes_pasado.isoformat()
            fechas['hasta'] = ultimo_dia_mes_pasado.isoformat()
        elif 'año pasado' in texto or 'último año' in texto or 'last year' in texto:
            hoy = datetime.now().date()
            fechas['desde'] = hoy.replace(year=hoy.year - 1, month=1, day=1).isoformat()
            fechas['hasta'] = hoy.replace(year=hoy.year - 1, month=12, day=31).isoformat()
        
        # Detectar fechas específicas
        fecha_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', texto)
        if fecha_match:
            dia, mes, anio = map(int, fecha_match.groups())
            try:
                fecha = datetime(anio, mes, dia).date()
                fechas['desde'] = fecha.isoformat()
                fechas['hasta'] = fecha.isoformat()
            except:
                pass
        
        # Detectar rango de fechas
        rango_match = re.search(r'desde\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+hasta\s+(\d{1,2})/(\d{1,2})/(\d{4})', texto)
        if rango_match:
            dia1, mes1, anio1, dia2, mes2, anio2 = map(int, rango_match.groups())
            try:
                fechas['desde'] = datetime(anio1, mes1, dia1).date().isoformat()
                fechas['hasta'] = datetime(anio2, mes2, dia2).date().isoformat()
            except:
                pass
        
        return fechas
    
    def _detectar_agrupacion(self, texto: str) -> List[str]:
        """Detecta cómo se quiere agrupar los datos"""
        agrupacion = []
        
        if 'por día' in texto or 'por día' in texto or 'diario' in texto:
            agrupacion.append('dia')
        elif 'por semana' in texto or 'semanal' in texto:
            agrupacion.append('semana')
        elif 'por mes' in texto or 'mensual' in texto:
            agrupacion.append('mes')
        elif 'por año' in texto or 'anual' in texto:
            agrupacion.append('año')
        
        if 'por categoría' in texto or 'por categoria' in texto:
            agrupacion.append('categoria')
        elif 'por producto' in texto:
            agrupacion.append('producto')
        elif 'por cliente' in texto:
            agrupacion.append('cliente')
        
        return agrupacion if agrupacion else []
    
    def _detectar_formato(self, texto: str) -> str:
        """Detecta el formato deseado del reporte"""
        if 'pdf' in texto or 'PDF' in texto:
            return 'pdf'
        elif 'excel' in texto or 'Excel' in texto or 'xlsx' in texto:
            return 'excel'
        elif 'pantalla' in texto or 'ver' in texto or 'mostrar' in texto:
            return 'pantalla'
        return 'pantalla'  # Por defecto
    
    def procesar_audio(self, audio_data: bytes) -> str:
        """
        Procesa audio y convierte a texto
        Por ahora, retorna texto simulado
        En producción, usar servicios como Google Speech-to-Text o Azure Speech
        """
        # TODO: Implementar conversión de audio a texto
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

