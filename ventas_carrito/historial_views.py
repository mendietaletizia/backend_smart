"""
CU13: Historial de Ventas
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Sum, Count, Avg, Max, Min
from productos.models import Producto, Categoria
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from .models import Venta, DetalleVenta, VentaHistorico
from autenticacion_usuarios.models import Usuario, Cliente, Bitacora

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
            producto_id = request.GET.get('producto_id')
            producto_nombre = request.GET.get('producto_nombre')  # Búsqueda por nombre
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
            
            # Filtrar por producto (ID)
            if producto_id:
                ventas_query = ventas_query.filter(
                    detalles__producto_id=producto_id
                ).distinct()
            
            # Filtrar por nombre de producto (búsqueda parcial, case-insensitive)
            if producto_nombre:
                ventas_query = ventas_query.filter(
                    detalles__producto__nombre__icontains=producto_nombre
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
            
            # Obtener información del usuario para el frontend
            user_role = usuario.id_rol.nombre.lower() if usuario.id_rol else 'cliente'
            
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
                'estadisticas': estadisticas,
                'user_role': user_role  # Información del rol para el frontend
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error en HistorialVentasView.get: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class HistorialFiltrosView(View):
    """
    Vista auxiliar para obtener opciones de filtros
    Retorna listas de clientes y productos para usar en filtros
    """
    
    def get(self, request):
        """Obtener opciones para filtros"""
        try:
            # Verificar autenticación
            if not request.session.get('is_authenticated'):
                return JsonResponse({
                    'success': False,
                    'message': 'Debe iniciar sesión'
                }, status=401)
            
            user_id = request.session.get('user_id')
            try:
                usuario = Usuario.objects.get(id=user_id)
                is_admin = usuario.id_rol.nombre.lower() == 'administrador'
            except Usuario.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }, status=404)
            
            response_data = {
                'success': True,
                'is_admin': is_admin
            }
            
            # Solo admin puede ver lista de clientes
            if is_admin:
                clientes = Cliente.objects.select_related('id').all().order_by('id__nombre')
                clientes_list = [
                    {
                        'id': cliente.id.id,
                        'nombre': f"{cliente.id.nombre} {cliente.id.apellido or ''}".strip(),
                        'email': cliente.id.email
                    }
                    for cliente in clientes
                ]
                response_data['clientes'] = clientes_list
            
            # Obtener lista de productos para filtro
            from productos.models import Producto
            productos = Producto.objects.all().order_by('nombre')[:100]  # Limitar a 100
            productos_list = [
                {
                    'id': producto.id,
                    'nombre': producto.nombre
                }
                for producto in productos
            ]
            response_data['productos'] = productos_list
            
            # Obtener categorías para filtro
            from productos.models import Categoria
            categorias = Categoria.objects.all().order_by('nombre')
            categorias_list = [
                {
                    'id': categoria.id_categoria,
                    'nombre': categoria.nombre
                }
                for categoria in categorias
            ]
            response_data['categorias'] = categorias_list
            
            # Métodos de pago disponibles - Solo Stripe
            response_data['metodos_pago'] = [
                {'value': 'stripe', 'label': 'Pago con Tarjeta (Stripe)'}
            ]
            
            # Estados disponibles
            response_data['estados'] = [
                {'value': 'pendiente', 'label': 'Pendiente'},
                {'value': 'completada', 'label': 'Completada'},
                {'value': 'cancelada', 'label': 'Cancelada'}
            ]
            
            return JsonResponse(response_data, status=200)
            
        except Exception as e:
            logger.error(f"Error en HistorialFiltrosView.get: {str(e)}", exc_info=True)
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


@method_decorator(csrf_exempt, name='dispatch')
class DashboardStatsView(View):
    """
    Vista para obtener estadísticas del dashboard del administrador
    """
    
    def get(self, request):
        """Obtener estadísticas del dashboard"""
        try:
            # Verificar autenticación
            if not request.session.get('is_authenticated'):
                return JsonResponse({
                    'success': False,
                    'message': 'Debe iniciar sesión'
                }, status=401)
            
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Sesión inválida. Por favor, inicie sesión nuevamente.'
                }, status=401)
            
            try:
                usuario = Usuario.objects.select_related('id_rol').get(id=user_id)
                rol_nombre = usuario.id_rol.nombre.lower() if usuario.id_rol else None
                is_admin = rol_nombre == 'administrador'
            except Usuario.DoesNotExist:
                logger.error(f"DashboardStatsView: Usuario con id {user_id} no encontrado")
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }, status=404)
            except Exception as e:
                logger.error(f"DashboardStatsView: Error al obtener usuario: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error al verificar usuario: {str(e)}'
                }, status=500)
            
            if not is_admin:
                return JsonResponse({
                    'success': False,
                    'message': 'Solo administradores pueden ver estadísticas del dashboard'
                }, status=403)
            
            # Fechas para comparación
            ahora = timezone.now()
            inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calcular inicio del mes anterior
            if inicio_mes_actual.month == 1:
                inicio_mes_anterior = inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12, day=1)
            else:
                inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1, day=1)
            
            fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
            
            # Ventas del mes actual
            ventas_mes_actual = Venta.objects.filter(fecha_venta__gte=inicio_mes_actual, estado='completada')
            total_ventas_mes = float(ventas_mes_actual.aggregate(Sum('total'))['total__sum'] or 0)
            cantidad_ventas_mes = ventas_mes_actual.count()
            
            # Ventas del mes anterior
            ventas_mes_anterior = Venta.objects.filter(
                fecha_venta__gte=inicio_mes_anterior,
                fecha_venta__lte=fin_mes_anterior,
                estado='completada'
            )
            total_ventas_mes_anterior = float(ventas_mes_anterior.aggregate(Sum('total'))['total__sum'] or 0)
            cantidad_ventas_mes_anterior = ventas_mes_anterior.count()
            
            # Calcular cambios porcentuales
            cambio_ventas = 0
            if total_ventas_mes_anterior > 0:
                cambio_ventas = ((total_ventas_mes - total_ventas_mes_anterior) / total_ventas_mes_anterior) * 100
            
            cambio_pedidos = 0
            if cantidad_ventas_mes_anterior > 0:
                cambio_pedidos = ((cantidad_ventas_mes - cantidad_ventas_mes_anterior) / cantidad_ventas_mes_anterior) * 100
            
            # Nuevos clientes este mes - usar bitácora para determinar fecha de registro
            clientes_mes_actual = Bitacora.objects.filter(
                accion='REGISTRO_CLIENTE',
                fecha__gte=inicio_mes_actual
            ).count()
            
            # Nuevos clientes mes anterior
            clientes_mes_anterior = Bitacora.objects.filter(
                accion='REGISTRO_CLIENTE',
                fecha__gte=inicio_mes_anterior,
                fecha__lte=fin_mes_anterior
            ).count()
            
            cambio_clientes = 0
            if clientes_mes_anterior > 0:
                cambio_clientes = ((clientes_mes_actual - clientes_mes_anterior) / clientes_mes_anterior) * 100
            
            # Productos disponibles (todos los productos en el sistema)
            productos_activos = Producto.objects.count()
            # Para el cambio porcentual, usamos el mismo valor ya que no hay historial
            productos_activos_anterior = productos_activos
            cambio_productos = 0.0
            
            # Ventas recientes (últimas 5)
            ventas_recientes = Venta.objects.select_related('cliente', 'cliente__id').order_by('-fecha_venta')[:5]
            ventas_recientes_data = []
            for venta in ventas_recientes:
                try:
                    cliente_nombre = 'Cliente desconocido'
                    if venta.cliente and venta.cliente.id:
                        nombre = venta.cliente.id.nombre or ''
                        apellido = venta.cliente.id.apellido or ''
                        cliente_nombre = f"{nombre} {apellido}".strip() or 'Cliente sin nombre'
                    
                    ventas_recientes_data.append({
                        'id': f'V-{venta.id_venta}',
                        'client': cliente_nombre,
                        'amount': float(venta.total or 0),
                        'status': venta.estado or 'pendiente',
                        'date': venta.fecha_venta.strftime('%d/%m/%Y') if venta.fecha_venta else 'Fecha desconocida'
                    })
                except Exception as e:
                    logger.warning(f"Error procesando venta {venta.id_venta}: {str(e)}")
                    continue
            
            # Productos más vendidos (top 4)
            productos_top = DetalleVenta.objects.filter(
                producto__isnull=False
            ).values(
                'producto__nombre', 'producto__precio'
            ).annotate(
                total_vendido=Sum('cantidad'),
                monto_total=Sum('subtotal')
            ).order_by('-total_vendido')[:4]
            
            top_products_data = []
            for prod in productos_top:
                if prod.get('producto__nombre'):
                    top_products_data.append({
                        'name': prod['producto__nombre'],
                        'sales': prod.get('total_vendido', 0),
                        'revenue': float(prod.get('monto_total') or 0)
                    })
            
            # Ventas mensuales para gráfico (últimos 12 meses)
            ventas_mensuales = []
            for i in range(11, -1, -1):
                mes_inicio = (ahora - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if i == 0:
                    mes_fin = ahora
                else:
                    siguiente_mes = mes_inicio + timedelta(days=32)
                    mes_fin = siguiente_mes.replace(day=1) - timedelta(seconds=1)
                
                ventas_mes = Venta.objects.filter(
                    fecha_venta__gte=mes_inicio,
                    fecha_venta__lte=mes_fin,
                    estado='completada'
                )
                total_mes = float(ventas_mes.aggregate(Sum('total'))['total__sum'] or 0)
                ventas_mensuales.append({
                    'mes': mes_inicio.strftime('%b'),
                    'total': total_mes
                })
            
            # Calcular altura relativa para el gráfico (0-100%)
            max_ventas = max([v['total'] for v in ventas_mensuales]) if ventas_mensuales else 1
            ventas_mensuales_alturas = [
                int((v['total'] / max_ventas) * 100) if max_ventas > 0 else 0
                for v in ventas_mensuales
            ]
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'ventas_mes': {
                        'value': total_ventas_mes,
                        'change': cambio_ventas,
                        'trend': 'up' if cambio_ventas >= 0 else 'down'
                    },
                    'total_pedidos': {
                        'value': cantidad_ventas_mes,
                        'change': cambio_pedidos,
                        'trend': 'up' if cambio_pedidos >= 0 else 'down'
                    },
                    'nuevos_clientes': {
                        'value': clientes_mes_actual,
                        'change': cambio_clientes,
                        'trend': 'up' if cambio_clientes >= 0 else 'down'
                    },
                    'productos_activos': {
                        'value': productos_activos,
                        'change': cambio_productos,
                        'trend': 'down' if cambio_productos < 0 else 'up'
                    }
                },
                'ventas_recientes': ventas_recientes_data,
                'top_products': top_products_data,
                'ventas_mensuales': {
                    'labels': [v['mes'] for v in ventas_mensuales],
                    'heights': ventas_mensuales_alturas,
                    'values': [v['total'] for v in ventas_mensuales]
                }
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error en DashboardStatsView.get: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)

