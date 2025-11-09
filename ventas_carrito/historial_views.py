"""
CU13: Historial de Ventas
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from .models import Venta, DetalleVenta, VentaHistorico
from autenticacion_usuarios.models import Usuario, Cliente

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class HistorialVentasView(View):
    """
    CU13: Historial de Ventas
    Permite consultar el historial de ventas con filtros y paginación
    """
    
    def get(self, request):
        """Obtener historial de ventas"""
        try:
            # Verificar autenticación
            if not request.session.get('is_authenticated'):
                return JsonResponse({
                    'success': False,
                    'message': 'Debe iniciar sesión para ver historial'
                }, status=401)
            
            # Obtener parámetros de filtro
            fecha_desde = request.GET.get('fecha_desde')
            fecha_hasta = request.GET.get('fecha_hasta')
            estado = request.GET.get('estado')
            metodo_pago = request.GET.get('metodo_pago')
            categoria_id = request.GET.get('categoria_id')
            cliente_id = request.GET.get('cliente_id')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            
            # Obtener usuario y cliente
            user_id = request.session.get('user_id')
            try:
                usuario = Usuario.objects.get(id=user_id)
                
                # Si es cliente, solo puede ver sus propias ventas
                if usuario.id_rol.nombre.lower() == 'cliente':
                    try:
                        cliente = Cliente.objects.get(id=usuario)
                        ventas_query = Venta.objects.filter(cliente=cliente)
                    except Cliente.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'message': 'Cliente no encontrado'
                        }, status=404)
                else:
                    # Admin puede ver todas las ventas o filtrar por cliente
                    ventas_query = Venta.objects.all()
                    if cliente_id:
                        try:
                            cliente = Cliente.objects.get(id=cliente_id)
                            ventas_query = ventas_query.filter(cliente=cliente)
                        except Cliente.DoesNotExist:
                            pass
            except Usuario.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }, status=404)
            
            # Aplicar filtros
            if fecha_desde:
                try:
                    fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
                    ventas_query = ventas_query.filter(fecha_venta__gte=fecha_desde_obj)
                except ValueError:
                    pass
            
            if fecha_hasta:
                try:
                    fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
                    # Agregar un día para incluir todo el día
                    fecha_hasta_obj += timedelta(days=1)
                    ventas_query = ventas_query.filter(fecha_venta__lt=fecha_hasta_obj)
                except ValueError:
                    pass
            
            if estado:
                ventas_query = ventas_query.filter(estado=estado)
            
            if metodo_pago:
                ventas_query = ventas_query.filter(metodo_pago=metodo_pago)
            
            # Filtrar por categoría (requiere join con detalles)
            if categoria_id:
                ventas_query = ventas_query.filter(
                    detalles__producto__categoria_id=categoria_id
                ).distinct()
            
            # Ordenar por fecha descendente
            ventas_query = ventas_query.select_related('cliente', 'cliente__id').prefetch_related(
                'detalles', 'detalles__producto'
            ).order_by('-fecha_venta')
            
            # Paginación
            paginator = Paginator(ventas_query, page_size)
            total_pages = paginator.num_pages
            total_ventas = paginator.count
            
            if page > total_pages:
                page = total_pages
            
            ventas_page = paginator.get_page(page)
            
            # Serializar ventas
            ventas_data = []
            for venta in ventas_page:
                detalles = venta.detalles.all()
                ventas_data.append({
                    'id': venta.id_venta,
                    'cliente': {
                        'id': venta.cliente.id.id,
                        'nombre': f"{venta.cliente.id.nombre} {venta.cliente.id.apellido or ''}".strip(),
                        'email': venta.cliente.id.email
                    },
                    'fecha': venta.fecha_venta.isoformat(),
                    'total': float(venta.total),
                    'estado': venta.estado,
                    'metodo_pago': venta.metodo_pago,
                    'direccion_entrega': venta.direccion_entrega,
                    'productos_count': detalles.count(),
                    'productos': [
                        {
                            'id': detalle.producto.id if detalle.producto else detalle.producto_id,
                            'nombre': detalle.producto.nombre if detalle.producto else f"Producto #{detalle.producto_id}",
                            'cantidad': detalle.cantidad,
                            'precio_unitario': float(detalle.precio_unitario),
                            'subtotal': float(detalle.subtotal)
                        }
                        for detalle in detalles
                    ],
                    'comprobante': {
                        'existe': hasattr(venta, 'comprobante'),
                        'numero': venta.comprobante.nro if hasattr(venta, 'comprobante') else None,
                        'pdf_url': f'/api/ventas/comprobantes/{venta.id_venta}/pdf/' if hasattr(venta, 'comprobante') else None
                    } if hasattr(venta, 'comprobante') else None,
                    'pago_online': {
                        'existe': hasattr(venta, 'pago_online'),
                        'estado': venta.pago_online.estado if hasattr(venta, 'pago_online') else None,
                        'referencia': venta.pago_online.referencia if hasattr(venta, 'pago_online') else None
                    } if hasattr(venta, 'pago_online') else None
                })
            
            # Calcular estadísticas
            estadisticas = {
                'total_ventas': total_ventas,
                'total_monto': float(ventas_query.aggregate(Sum('total'))['total__sum'] or 0),
                'ventas_completadas': ventas_query.filter(estado='completada').count(),
                'ventas_pendientes': ventas_query.filter(estado='pendiente').count(),
                'ventas_canceladas': ventas_query.filter(estado='cancelada').count(),
            }
            
            return JsonResponse({
                'success': True,
                'ventas': ventas_data,
                'paginacion': {
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'total_ventas': total_ventas,
                    'has_next': ventas_page.has_next(),
                    'has_previous': ventas_page.has_previous()
                },
                'estadisticas': estadisticas
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error en HistorialVentasView.get: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class HistorialAgregadoView(View):
    """
    CU13: Historial Agregado de Ventas
    Retorna datos históricos agregados por fecha y categoría
    """
    
    def get(self, request):
        """Obtener historial agregado"""
        try:
            # Verificar autenticación (solo admin)
            if not request.session.get('is_authenticated'):
                return JsonResponse({
                    'success': False,
                    'message': 'Debe iniciar sesión'
                }, status=401)
            
            user_id = request.session.get('user_id')
            usuario = Usuario.objects.get(id=user_id)
            
            if usuario.id_rol.nombre.lower() != 'administrador':
                return JsonResponse({
                    'success': False,
                    'message': 'Solo administradores pueden ver historial agregado'
                }, status=403)
            
            # Parámetros
            fecha_desde = request.GET.get('fecha_desde')
            fecha_hasta = request.GET.get('fecha_hasta')
            categoria_id = request.GET.get('categoria_id')
            agrupar_por = request.GET.get('agrupar_por', 'dia')  # dia, semana, mes
            
            # Obtener historial
            historial_query = VentaHistorico.objects.all()
            
            if fecha_desde:
                try:
                    fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                    historial_query = historial_query.filter(fecha__gte=fecha_desde_obj)
                except ValueError:
                    pass
            
            if fecha_hasta:
                try:
                    fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                    historial_query = historial_query.filter(fecha__lte=fecha_hasta_obj)
                except ValueError:
                    pass
            
            if categoria_id:
                historial_query = historial_query.filter(categoria_id=categoria_id)
            
            historial_query = historial_query.select_related('categoria').order_by('-fecha')
            
            # Serializar
            historial_data = []
            for hist in historial_query:
                historial_data.append({
                    'id': hist.id_his,
                    'fecha': hist.fecha.isoformat(),
                    'categoria': {
                        'id': hist.categoria.id_categoria if hist.categoria else None,
                        'nombre': hist.categoria.nombre if hist.categoria else 'General'
                    },
                    'cantidad_total': hist.cantidad_total,
                    'monto_total': float(hist.monto_total),
                    'ventas_count': hist.ventas_count
                })
            
            return JsonResponse({
                'success': True,
                'historial': historial_data,
                'total_registros': len(historial_data)
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error en HistorialAgregadoView.get: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SincronizarHistorialView(View):
    """
    CU13: Sincronizar Historial
    Genera o actualiza registros de historial agregado desde ventas
    """
    
    def post(self, request):
        """Sincronizar historial desde ventas"""
        try:
            # Solo admin
            if not request.session.get('is_authenticated'):
                return JsonResponse({
                    'success': False,
                    'message': 'Debe iniciar sesión'
                }, status=401)
            
            user_id = request.session.get('user_id')
            usuario = Usuario.objects.get(id=user_id)
            
            if usuario.id_rol.nombre.lower() != 'administrador':
                return JsonResponse({
                    'success': False,
                    'message': 'Solo administradores pueden sincronizar historial'
                }, status=403)
            
            # Obtener ventas completadas
            ventas = Venta.objects.filter(estado='completada').select_related(
                'cliente'
            ).prefetch_related('detalles', 'detalles__producto', 'detalles__producto__categoria')
            
            registros_creados = 0
            
            # Agrupar por fecha y categoría
            from collections import defaultdict
            agrupacion = defaultdict(lambda: {
                'cantidad_total': 0,
                'monto_total': 0,
                'ventas_count': 0
            })
            
            for venta in ventas:
                fecha = venta.fecha_venta.date()
                
                for detalle in venta.detalles.all():
                    categoria_id = None
                    if detalle.producto and detalle.producto.categoria:
                        categoria_id = detalle.producto.categoria.id_categoria
                    
                    key = (fecha, categoria_id)
                    agrupacion[key]['cantidad_total'] += detalle.cantidad
                    agrupacion[key]['monto_total'] += float(detalle.subtotal)
                
                # Contar ventas por fecha (sin categoría)
                key_general = (fecha, None)
                agrupacion[key_general]['ventas_count'] += 1
            
            # Crear o actualizar registros
            for (fecha, categoria_id), datos in agrupacion.items():
                historial, created = VentaHistorico.objects.update_or_create(
                    fecha=fecha,
                    categoria_id=categoria_id,
                    defaults={
                        'cantidad_total': datos['cantidad_total'],
                        'monto_total': datos['monto_total'],
                        'ventas_count': datos['ventas_count']
                    }
                )
                if created:
                    registros_creados += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Historial sincronizado. {registros_creados} registros creados/actualizados.',
                'registros_procesados': len(agrupacion)
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error en SincronizarHistorialView.post: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)


