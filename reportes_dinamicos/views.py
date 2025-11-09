"""
CU14-CU20: Reportes Dinámicos
"""
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Sum, Count, Avg, Max, Min
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
import json
import logging
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from .models import Reporte, ModeloIA, PrediccionVenta
from .interpreter import ReporteInterpreter
from ventas_carrito.models import Venta, DetalleVenta
from productos.models import Producto, Categoria
from autenticacion_usuarios.models import Usuario, Cliente

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class SolicitarReporteView(View):
    """
    CU14: Solicitar Reporte por Texto
    CU15: Solicitar Reporte por Voz
    CU16: Interpretar Solicitud
    """
    
    def post(self, request):
        """Procesar solicitud de reporte (texto o voz)"""
        try:
            # Verificar autenticación
            if not request.session.get('is_authenticated'):
                return JsonResponse({
                    'success': False,
                    'message': 'Debe iniciar sesión para generar reportes'
                }, status=401)
            
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no autenticado'
                }, status=401)
            
            try:
                usuario = Usuario.objects.get(id=user_id)
            except Usuario.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }, status=404)
            
            # Obtener datos
            data = json.loads(request.body)
            texto = data.get('texto')
            audio_data = data.get('audio')  # Base64 o bytes
            
            # Si hay audio, procesarlo primero
            if audio_data:
                # CU15: Procesar voz
                # Por ahora, esperamos que el frontend envíe el texto transcrito
                texto = data.get('texto_transcrito') or texto
            
            if not texto:
                return JsonResponse({
                    'success': False,
                    'message': 'Texto de solicitud requerido'
                }, status=400)
            
            # CU16: Interpretar solicitud
            try:
                interpreter = ReporteInterpreter()
                parametros = interpreter.interpretar(texto)
            except Exception as e:
                logger.error(f"Error al interpretar solicitud: {str(e)}", exc_info=True)
                return JsonResponse({
                    'success': False,
                    'message': f'Error al interpretar la solicitud: {str(e)}'
                }, status=400)
            
            # Generar reporte
            try:
                generador = GeneradorReporte()
                reporte_data = generador.generar(parametros, usuario)
            except Exception as e:
                logger.error(f"Error al generar reporte: {str(e)}", exc_info=True)
                return JsonResponse({
                    'success': False,
                    'message': f'Error al generar el reporte: {str(e)}'
                }, status=500)
            
            # Convertir fechas a strings para JSON serialization
            parametros_serializados = self._serializar_parametros(parametros)
            
            # Guardar reporte
            reporte = Reporte.objects.create(
                nombre=f"Reporte {parametros['tipo_reporte']} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                tipo=parametros['tipo_reporte'],
                descripcion=f"Generado desde: {texto}",
                parametros=parametros_serializados,
                prompt=texto,
                formato=parametros.get('formato', 'pantalla'),
                origen_comando='voz' if audio_data else 'texto',
                id_usuario=usuario,
                datos=reporte_data,
                estado='completado'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Reporte generado exitosamente',
                'reporte': {
                    'id': reporte.id_reporte,
                    'nombre': reporte.nombre,
                    'tipo': reporte.tipo,
                    'formato': reporte.formato,
                    'datos': reporte_data,
                    'fecha': reporte.fecha_generacion.isoformat(),
                    'parametros': parametros
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de datos inválido'
            }, status=400)
        except Exception as e:
            logger.error(f"Error en SolicitarReporteView.post: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)
    
    def _serializar_parametros(self, parametros: dict) -> dict:
        """Convierte objetos date/datetime a strings para JSON serialization"""
        import copy
        from datetime import date, datetime
        
        parametros_serializados = copy.deepcopy(parametros)
        
        # Convertir fechas en el diccionario de fechas
        if 'fechas' in parametros_serializados:
            fechas = parametros_serializados['fechas']
            if isinstance(fechas, dict):
                for key in ['desde', 'hasta']:
                    if key in fechas:
                        fecha_val = fechas[key]
                        if isinstance(fecha_val, (date, datetime)):
                            fechas[key] = fecha_val.isoformat()
                        elif not isinstance(fecha_val, str):
                            # Si es otro tipo, intentar convertirlo
                            try:
                                fechas[key] = str(fecha_val)
                            except:
                                if key in fechas:
                                    del fechas[key]
        
        return parametros_serializados


class GeneradorReporte:
    """Generador de reportes dinámicos"""
    
    def generar(self, parametros: dict, usuario: Usuario) -> dict:
        """Genera reporte según parámetros"""
        tipo = parametros.get('tipo_reporte', 'general')
        
        if tipo == 'ventas':
            return self._generar_reporte_ventas(parametros, usuario)
        elif tipo == 'productos':
            return self._generar_reporte_productos(parametros, usuario)
        elif tipo == 'clientes':
            return self._generar_reporte_clientes(parametros, usuario)
        elif tipo == 'inventario':
            return self._generar_reporte_inventario(parametros, usuario)
        elif tipo == 'financiero':
            return self._generar_reporte_financiero(parametros, usuario)
        else:
            return self._generar_reporte_general(parametros, usuario)
    
    def _generar_reporte_ventas(self, parametros: dict, usuario: Usuario) -> dict:
        """CU17: Generar reporte de ventas"""
        query = Venta.objects.select_related('cliente', 'cliente__id').prefetch_related(
            'detalles', 'detalles__producto'
        )
        
        # Aplicar filtros
        filtros = parametros.get('filtros', {})
        if 'estado' in filtros:
            query = query.filter(estado=filtros['estado'])
        if 'metodo_pago' in filtros:
            query = query.filter(metodo_pago=filtros['metodo_pago'])
        
        # Aplicar fechas con manejo robusto
        fechas = parametros.get('fechas', {})
        if 'desde' in fechas and fechas['desde']:
            try:
                desde_date = fechas['desde']
                if isinstance(desde_date, str):
                    try:
                        desde_date = datetime.fromisoformat(desde_date.replace('Z', '+00:00'))
                    except:
                        desde_date = datetime.strptime(desde_date, '%Y-%m-%d')
                query = query.filter(fecha_venta__gte=desde_date)
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(f"Error al parsear fecha 'desde': {str(e)}")
        if 'hasta' in fechas and fechas['hasta']:
            try:
                hasta_date = fechas['hasta']
                if isinstance(hasta_date, str):
                    try:
                        hasta_date = datetime.fromisoformat(hasta_date.replace('Z', '+00:00'))
                    except:
                        hasta_date = datetime.strptime(hasta_date, '%Y-%m-%d')
                query = query.filter(fecha_venta__lte=hasta_date)
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(f"Error al parsear fecha 'hasta': {str(e)}")
        
        # Agrupar si es necesario
        agrupacion = parametros.get('agrupacion', [])
        metricas = parametros.get('metricas', ['total'])
        
        if 'categoria' in agrupacion:
            # Agrupar por categoría
            datos = []
            categorias = Categoria.objects.all()
            for categoria in categorias:
                ventas_cat = query.filter(detalles__producto__categoria=categoria).distinct()
                datos.append({
                    'categoria': categoria.nombre,
                    'total_ventas': ventas_cat.count(),
                    'monto_total': float(ventas_cat.aggregate(Sum('total'))['total__sum'] or 0)
                })
            return {
                'tipo': 'ventas',
                'agrupacion': 'categoria',
                'datos': datos,
                'total_general': float(query.aggregate(Sum('total'))['total__sum'] or 0),
                'cantidad_ventas': query.count()
            }
        else:
            # Datos sin agrupar
            ventas = query.order_by('-fecha_venta')[:100]  # Limitar a 100
            datos = []
            for venta in ventas:
                datos.append({
                    'id': venta.id_venta,
                    'fecha': venta.fecha_venta.isoformat(),
                    'cliente': f"{venta.cliente.id.nombre} {venta.cliente.id.apellido or ''}".strip(),
                    'total': float(venta.total),
                    'estado': venta.estado,
                    'metodo_pago': venta.metodo_pago,
                    'productos_count': venta.detalles.count()
                })
            
            return {
                'tipo': 'ventas',
                'datos': datos,
                'total_general': float(query.aggregate(Sum('total'))['total__sum'] or 0),
                'cantidad_ventas': query.count(),
                'promedio_venta': float(query.aggregate(Avg('total'))['total__avg'] or 0)
            }
    
    def _generar_reporte_productos(self, parametros: dict, usuario: Usuario) -> dict:
        """Generar reporte de productos"""
        query = Producto.objects.select_related('categoria', 'marca', 'proveedor')
        
        # Aplicar filtros
        filtros = parametros.get('filtros', {})
        if 'categoria' in filtros:
            query = query.filter(categoria__nombre__icontains=filtros['categoria'])
        
        productos = query.order_by('nombre')[:100]
        
        datos = []
        for producto in productos:
            from productos.models import Stock
            stock = Stock.objects.filter(producto=producto).first()
            datos.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
                'precio': float(producto.precio),
                'stock': stock.cantidad if stock else 0,
                'marca': producto.marca.nombre if producto.marca else 'Sin marca'
            })
        
        return {
            'tipo': 'productos',
            'datos': datos,
            'total_productos': query.count()
        }
    
    def _generar_reporte_clientes(self, parametros: dict, usuario: Usuario) -> dict:
        """Generar reporte de clientes"""
        query = Cliente.objects.select_related('id')
        
        clientes = query.order_by('id__nombre')[:100]
        
        datos = []
        for cliente in clientes:
            ventas_count = Venta.objects.filter(cliente=cliente).count()
            total_compras = float(Venta.objects.filter(cliente=cliente).aggregate(Sum('total'))['total__sum'] or 0)
            
            datos.append({
                'id': cliente.id.id,
                'nombre': f"{cliente.id.nombre} {cliente.id.apellido or ''}".strip(),
                'email': cliente.id.email,
                'telefono': cliente.id.telefono,
                'direccion': cliente.direccion,
                'ciudad': cliente.ciudad,
                'ventas_count': ventas_count,
                'total_compras': total_compras
            })
        
        return {
            'tipo': 'clientes',
            'datos': datos,
            'total_clientes': query.count()
        }
    
    def _generar_reporte_inventario(self, parametros: dict, usuario: Usuario) -> dict:
        """Generar reporte de inventario"""
        from productos.models import Stock
        
        query = Stock.objects.select_related('producto', 'producto__categoria')
        
        stocks = query.order_by('producto__nombre')[:100]
        
        datos = []
        for stock in stocks:
            datos.append({
                'producto_id': stock.producto.id,
                'producto_nombre': stock.producto.nombre,
                'categoria': stock.producto.categoria.nombre if stock.producto.categoria else 'Sin categoría',
                'cantidad': stock.cantidad,
                'fecha_actualizacion': stock.fecha_actualizacion.isoformat()
            })
        
        return {
            'tipo': 'inventario',
            'datos': datos,
            'total_productos': query.count()
        }
    
    def _generar_reporte_financiero(self, parametros: dict, usuario: Usuario) -> dict:
        """Generar reporte financiero"""
        query = Venta.objects.filter(estado='completada')
        
        # Aplicar fechas
        fechas = parametros.get('fechas', {})
        if 'desde' in fechas:
            query = query.filter(fecha_venta__gte=fechas['desde'])
        if 'hasta' in fechas:
            query = query.filter(fecha_venta__lte=fechas['hasta'])
        
        total_ingresos = float(query.aggregate(Sum('total'))['total__sum'] or 0)
        cantidad_ventas = query.count()
        promedio_venta = float(query.aggregate(Avg('total'))['total__avg'] or 0)
        
        # Por método de pago
        por_metodo = {}
        for metodo in ['efectivo', 'tarjeta_credito', 'transferencia']:
            ventas_metodo = query.filter(metodo_pago=metodo)
            por_metodo[metodo] = {
                'cantidad': ventas_metodo.count(),
                'total': float(ventas_metodo.aggregate(Sum('total'))['total__sum'] or 0)
            }
        
        return {
            'tipo': 'financiero',
            'total_ingresos': total_ingresos,
            'cantidad_ventas': cantidad_ventas,
            'promedio_venta': promedio_venta,
            'por_metodo_pago': por_metodo
        }
    
    def _generar_reporte_general(self, parametros: dict, usuario: Usuario) -> dict:
        """Generar reporte general"""
        return {
            'tipo': 'general',
            'mensaje': 'Reporte general',
            'parametros': parametros
        }


@method_decorator(csrf_exempt, name='dispatch')
class DescargarReporteView(View):
    """
    CU18: Generar Reporte en PDF o Excel
    CU20: Descargar o Visualizar Reporte
    """
    
    def get(self, request, reporte_id):
        """Descargar reporte en formato PDF o Excel"""
        try:
            formato = request.GET.get('formato', 'pdf')
            
            try:
                reporte = Reporte.objects.get(id_reporte=reporte_id)
            except Reporte.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Reporte no encontrado'
                }, status=404)
            
            if formato == 'pdf':
                return self._generar_pdf(reporte)
            elif formato == 'excel':
                return self._generar_excel(reporte)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato no soportado. Use pdf o excel'
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error en DescargarReporteView.get: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)
    
    def _generar_pdf(self, reporte: Reporte):
        """Generar PDF del reporte"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        story.append(Paragraph(f"<b>{reporte.nombre}</b>", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Información
        info_data = [
            ['Tipo:', reporte.get_tipo_display()],
            ['Fecha:', reporte.fecha_generacion.strftime('%d/%m/%Y %H:%M')],
            ['Formato:', reporte.get_formato_display()],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Datos
        datos = reporte.datos
        if isinstance(datos, dict) and 'datos' in datos:
            datos_lista = datos['datos']
            if datos_lista:
                # Encabezados
                headers = list(datos_lista[0].keys())
                tabla_data = [headers]
                
                # Filas
                for item in datos_lista[:50]:  # Limitar a 50
                    tabla_data.append([str(item.get(h, '')) for h in headers])
                
                tabla = Table(tabla_data, colWidths=[6*inch/len(headers)] * len(headers))
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(tabla)
        
        doc.build(story)
        buffer.seek(0)
        
        return HttpResponse(buffer, content_type='application/pdf')
    
    def _generar_excel(self, reporte: Reporte):
        """Generar Excel del reporte"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        
        # Título
        ws['A1'] = reporte.nombre
        ws['A1'].font = Font(bold=True, size=14)
        
        # Información
        ws['A3'] = 'Tipo:'
        ws['B3'] = reporte.get_tipo_display()
        ws['A4'] = 'Fecha:'
        ws['B4'] = reporte.fecha_generacion.strftime('%d/%m/%Y %H:%M')
        
        # Datos
        datos = reporte.datos
        if isinstance(datos, dict) and 'datos' in datos:
            datos_lista = datos['datos']
            if datos_lista:
                # Encabezados
                headers = list(datos_lista[0].keys())
                for col, header in enumerate(headers, 1):
                    cell = ws.cell(row=6, column=col)
                    cell.value = header
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                
                # Filas
                for row, item in enumerate(datos_lista[:1000], 7):  # Limitar a 1000
                    for col, header in enumerate(headers, 1):
                        ws.cell(row=row, column=col, value=str(item.get(header, '')))
        
        # Ajustar ancho de columnas
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


@method_decorator(csrf_exempt, name='dispatch')
class FiltrosInteligentesView(View):
    """
    CU19: Aplicar Filtros Inteligentes
    Usa IA para sugerir filtros relevantes
    """
    
    def post(self, request):
        """Obtener filtros inteligentes sugeridos"""
        try:
            data = json.loads(request.body)
            tipo_reporte = data.get('tipo_reporte', 'ventas')
            
            # Generar sugerencias usando análisis básico
            sugerencias = self._generar_sugerencias(tipo_reporte)
            
            return JsonResponse({
                'success': True,
                'sugerencias': sugerencias
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error en FiltrosInteligentesView.post: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)
    
    def _generar_sugerencias(self, tipo: str) -> list:
        """Generar sugerencias de filtros"""
        sugerencias = []
        
        if tipo == 'ventas':
            # Analizar tendencias
            hoy = timezone.now().date()
            semana_pasada = hoy - timedelta(days=7)
            
            ventas_semana = Venta.objects.filter(
                fecha_venta__gte=semana_pasada,
                estado='completada'
            ).count()
            
            if ventas_semana > 10:
                sugerencias.append({
                    'filtro': 'fecha',
                    'tipo': 'periodo',
                    'valor': 'última semana',
                    'razon': f'Se registraron {ventas_semana} ventas en la última semana'
                })
            
            # Categorías más vendidas
            from django.db.models import Sum
            categorias_vendidas = DetalleVenta.objects.filter(
                venta__fecha_venta__gte=semana_pasada,
                producto__categoria__isnull=False
            ).values('producto__categoria__nombre').annotate(
                total=Sum('subtotal')
            ).order_by('-total')[:3]
            
            for cat in categorias_vendidas:
                sugerencias.append({
                    'filtro': 'categoria',
                    'tipo': 'valor',
                    'valor': cat['producto__categoria__nombre'],
                    'razon': f'Categoría con mayor movimiento: ${cat["total"]:.2f}'
                })
        
        return sugerencias


@method_decorator(csrf_exempt, name='dispatch')
class ListarReportesView(View):
    """Listar reportes generados"""
    
    def get(self, request):
        """Listar reportes del usuario"""
        try:
            if not request.session.get('is_authenticated'):
                return JsonResponse({
                    'success': False,
                    'message': 'Debe iniciar sesión'
                }, status=401)
            
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no autenticado'
                }, status=401)
            
            try:
                usuario = Usuario.objects.get(id=user_id)
            except Usuario.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }, status=404)
            
            # Obtener reportes del usuario
            reportes = Reporte.objects.filter(id_usuario=usuario).order_by('-fecha_generacion')[:50]
            
            datos = []
            for reporte in reportes:
                datos.append({
                    'id': reporte.id_reporte,
                    'nombre': reporte.nombre,
                    'tipo': reporte.tipo,
                    'formato': reporte.formato,
                    'fecha': reporte.fecha_generacion.isoformat(),
                    'origen': reporte.get_origen_comando_display(),
                    'pdf_url': f'/api/reportes/{reporte.id_reporte}/descargar/?formato=pdf' if reporte.formato == 'pdf' else None,
                    'excel_url': f'/api/reportes/{reporte.id_reporte}/descargar/?formato=excel'
                })
            
            return JsonResponse({
                'success': True,
                'reportes': datos
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error en ListarReportesView.get: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)
