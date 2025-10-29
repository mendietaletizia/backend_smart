from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.sessions.models import Session
import json

from .models import Carrito, ItemCarrito, Venta, DetalleVenta
from productos.models import Producto


@method_decorator(csrf_exempt, name='dispatch')
class CarritoView(View):
    """CU8 y CU9: Gestión completa del carrito de compras"""
    
    def get(self, request):
        """Obtener el carrito del usuario"""
        try:
            carrito = self._get_or_create_carrito(request)
            
            items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
            
            data = {
                'carrito_id': carrito.id_carrito,
                'total_items': carrito.get_total_items(),
                'total_precio': float(carrito.get_total_precio()),
                'items': []
            }
            
            for item in items:
                data['items'].append({
                    'id': item.id_item,
                    'producto_id': item.producto.id,
                    'producto_nombre': item.producto.nombre,
                    'producto_imagen': item.producto.imagen,
                    'cantidad': item.cantidad,
                    'precio_unitario': float(item.precio_unitario),
                    'subtotal': float(item.get_subtotal()),
                })
            
            return JsonResponse({
                'success': True,
                'data': data
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    def post(self, request):
        """CU8: Añadir producto al carrito"""
        try:
            data = json.loads(request.body)
            producto_id = data.get('producto_id')
            cantidad = data.get('cantidad', 1)
            
            if not producto_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de producto requerido'
                }, status=400)
            
            try:
                producto = Producto.objects.get(id=producto_id)
            except Producto.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto no encontrado'
                }, status=404)
            
            # Validar cantidad
            if cantidad <= 0:
                return JsonResponse({
                    'success': False,
                    'message': 'La cantidad debe ser mayor a 0'
                }, status=400)
            
            # Obtener o crear carrito
            carrito = self._get_or_create_carrito(request)
            
            # Verificar si el producto ya está en el carrito
            item_existente = ItemCarrito.objects.filter(
                carrito=carrito,
                producto=producto
            ).first()
            
            if item_existente:
                # Actualizar cantidad del item existente
                item_existente.cantidad += cantidad
                item_existente.save()
                mensaje = f"Se agregaron {cantidad} unidades más de {producto.nombre}"
            else:
                # Crear nuevo item en el carrito
                ItemCarrito.objects.create(
                    carrito=carrito,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )
                mensaje = f"{producto.nombre} agregado al carrito"
            
            return JsonResponse({
                'success': True,
                'message': mensaje,
                'carrito_id': carrito.id_carrito,
                'total_items': carrito.total_items
            }, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    def put(self, request):
        """Actualizar cantidad de un item en el carrito"""
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            cantidad = data.get('cantidad')
            
            if not item_id or cantidad is None:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de item y cantidad requeridos'
                }, status=400)
            
            try:
                item = ItemCarrito.objects.get(id_item=item_id)
            except ItemCarrito.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Item no encontrado'
                }, status=404)
            
            if cantidad <= 0:
                # Eliminar el item si la cantidad es 0 o menor
                item.delete()
                mensaje = f"{item.producto.nombre} eliminado del carrito"
            else:
                item.cantidad = cantidad
                item.save()
                mensaje = f"Cantidad de {item.producto.nombre} actualizada"
            
            return JsonResponse({
                'success': True,
                'message': mensaje
            }, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    def delete(self, request):
        """Eliminar item del carrito"""
        try:
            item_id = request.GET.get('item_id')
            
            if not item_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de item requerido'
                }, status=400)
            
            try:
                item = ItemCarrito.objects.get(id_item=item_id)
                producto_nombre = item.producto.nombre
                item.delete()
                
                return JsonResponse({
                    'success': True,
                    'message': f"{producto_nombre} eliminado del carrito"
                }, status=200)
                
            except ItemCarrito.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Item no encontrado'
                }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    def _get_or_create_carrito(self, request):
        """Obtener o crear carrito para el usuario/sesión"""
        # Si el usuario está autenticado, usar su carrito
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                from autenticacion_usuarios.models import Cliente
                cliente = Cliente.objects.get(id=request.user)
                carrito, created = Carrito.objects.get_or_create(
                    cliente=cliente,
                    activo=True,
                    defaults={'session_key': None}
                )
                return carrito
            except:
                pass
        
        # Si no está autenticado, usar session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        carrito, created = Carrito.objects.get_or_create(
            session_key=session_key,
            activo=True,
            defaults={'cliente': None}
        )
        return carrito


@method_decorator(csrf_exempt, name='dispatch')
class CarritoManagementView(View):
    """CU9: Gestión avanzada del carrito"""
    
    def post(self, request):
        """CU9: Operaciones avanzadas del carrito"""
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'clear':
                return self._clear_carrito(request)
            elif action == 'merge':
                return self._merge_carritos(request, data)
            elif action == 'save_for_later':
                return self._save_for_later(request, data)
            elif action == 'apply_discount':
                return self._apply_discount(request, data)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Acción no válida'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    def _clear_carrito(self, request):
        """CU9: Limpiar completamente el carrito"""
        carrito = self._get_or_create_carrito(request)
        ItemCarrito.objects.filter(carrito=carrito).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Carrito limpiado exitosamente'
        }, status=200)

    def _merge_carritos(self, request, data):
        """CU9: Fusionar carritos (útil cuando un visitante se registra)"""
        carrito_origen_id = data.get('carrito_origen_id')
        
        if not carrito_origen_id:
            return JsonResponse({
                'success': False,
                'message': 'ID de carrito origen requerido'
            }, status=400)
        
        try:
            carrito_origen = Carrito.objects.get(id_carrito=carrito_origen_id)
            carrito_destino = self._get_or_create_carrito(request)
            
            # Mover items del carrito origen al destino
            items_origen = ItemCarrito.objects.filter(carrito=carrito_origen)
            items_movidos = 0
            
            for item in items_origen:
                # Verificar si el producto ya existe en el carrito destino
                item_existente = ItemCarrito.objects.filter(
                    carrito=carrito_destino,
                    producto=item.producto
                ).first()
                
                if item_existente:
                    # Sumar cantidades
                    item_existente.cantidad += item.cantidad
                    item_existente.save()
                else:
                    # Crear nuevo item
                    ItemCarrito.objects.create(
                        carrito=carrito_destino,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_unitario=item.precio_unitario
                    )
                items_movidos += 1
            
            # Eliminar carrito origen
            carrito_origen.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Carrito fusionado exitosamente. {items_movidos} items movidos.',
                'carrito_id': carrito_destino.id_carrito
            }, status=200)
            
        except Carrito.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Carrito origen no encontrado'
            }, status=404)

    def _save_for_later(self, request, data):
        """CU9: Guardar item para más tarde (marcar como favorito)"""
        item_id = data.get('item_id')
        
        if not item_id:
            return JsonResponse({
                'success': False,
                'message': 'ID de item requerido'
            }, status=400)
        
        try:
            item = ItemCarrito.objects.get(id_item=item_id)
            # Por ahora solo eliminamos del carrito, en el futuro se podría guardar en una tabla de favoritos
            producto_nombre = item.producto.nombre
            item.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'{producto_nombre} guardado para más tarde'
            }, status=200)
            
        except ItemCarrito.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Item no encontrado'
            }, status=404)

    def _apply_discount(self, request, data):
        """CU9: Aplicar descuento al carrito"""
        codigo_descuento = data.get('codigo_descuento')
        porcentaje = data.get('porcentaje', 0)
        
        if not codigo_descuento and not porcentaje:
            return JsonResponse({
                'success': False,
                'message': 'Código de descuento o porcentaje requerido'
            }, status=400)
        
        carrito = self._get_or_create_carrito(request)
        
        # Por simplicidad, aplicamos un descuento del 10% si se proporciona código
        if codigo_descuento:
            if codigo_descuento.upper() in ['DESCUENTO10', 'WELCOME10', 'PRIMERA10']:
                porcentaje = 10
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Código de descuento no válido'
                }, status=400)
        
        # Aplicar descuento a todos los items del carrito
        items = ItemCarrito.objects.filter(carrito=carrito)
        items_actualizados = 0
        
        for item in items:
            precio_original = item.producto.precio
            precio_descuento = precio_original * (1 - porcentaje / 100)
            item.precio_unitario = precio_descuento
            item.save()
            items_actualizados += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Descuento del {porcentaje}% aplicado a {items_actualizados} items',
            'descuento_aplicado': porcentaje
        }, status=200)

    def _get_or_create_carrito(self, request):
        """Método auxiliar para obtener o crear carrito"""
        # Si el usuario está autenticado, usar su carrito
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                from autenticacion_usuarios.models import Cliente
                cliente = Cliente.objects.get(id=request.user)
                carrito, created = Carrito.objects.get_or_create(
                    cliente=cliente,
                    activo=True,
                    defaults={'session_key': None}
                )
                return carrito
            except:
                pass
        
        # Si no está autenticado, usar session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        carrito, created = Carrito.objects.get_or_create(
            session_key=session_key,
            activo=True,
            defaults={'cliente': None}
        )
        return carrito