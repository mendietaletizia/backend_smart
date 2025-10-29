from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from .models import Carrito, ItemCarrito, Venta, DetalleVenta


# ==========================================================
# CASO DE USO 10: REALIZAR COMPRA (CHECKOUT)
# ==========================================================

@method_decorator(csrf_exempt, name='dispatch')
class CheckoutView(View):
    """
    CU10: Realizar Compra (Checkout)
    Permite a clientes autenticados realizar compras desde su carrito
    """
    
    def get(self, request):
        """Mostrar información del endpoint de checkout"""
        return JsonResponse({
            'endpoint': 'Checkout API',
            'method': 'POST',
            'description': 'Realizar compra desde el carrito',
            'required_fields': ['metodo_pago', 'direccion_entrega'],
            'optional_fields': ['notas'],
            'example': {
                'metodo_pago': 'efectivo',
                'direccion_entrega': 'Calle 123, #45, Ciudad',
                'notas': 'Entregar en horario de oficina'
            },
            'note': 'Requires authenticated user with items in cart'
        })
    
    def post(self, request):
        try:
            # Verificar que el usuario esté autenticado
            if not request.session.get('is_authenticated'):
                return JsonResponse({
                    'success': False,
                    'message': 'Debe iniciar sesión para realizar compras'
                }, status=401)
            
            # Obtener datos del request
            data = json.loads(request.body)
            metodo_pago = data.get('metodo_pago', 'efectivo')
            direccion_entrega = data.get('direccion_entrega', '')
            notas = data.get('notas', '')
            
            # Validaciones básicas
            if not direccion_entrega.strip():
                return JsonResponse({
                    'success': False,
                    'message': 'La dirección de entrega es obligatoria'
                }, status=400)
            
            # Obtener cliente autenticado
            user_id = request.session.get('user_id')
            try:
                from autenticacion_usuarios.models import Usuario, Cliente
                usuario = Usuario.objects.get(id=user_id)
                cliente = Cliente.objects.get(id=usuario)
            except (Usuario.DoesNotExist, Cliente.DoesNotExist):
                return JsonResponse({
                    'success': False,
                    'message': 'Cliente no encontrado'
                }, status=404)
            
            # Obtener carrito del cliente
            try:
                carrito = Carrito.objects.get(cliente=cliente, activo=True)
            except Carrito.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'No hay productos en el carrito'
                }, status=400)
            
            # Verificar que el carrito tenga items
            items_carrito = ItemCarrito.objects.filter(carrito=carrito)
            if not items_carrito.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'El carrito está vacío'
                }, status=400)
            
            # Calcular total
            total = sum(item.get_subtotal() for item in items_carrito)
            
            # Crear venta
            venta = Venta.objects.create(
                cliente=cliente,
                total=total,
                estado='pendiente',
                metodo_pago=metodo_pago,
                direccion_entrega=direccion_entrega,
                notas=notas
            )
            
            # Crear detalles de venta y actualizar stock
            detalles_creados = []
            for item in items_carrito:
                # Verificar stock disponible
                if item.producto.stock < item.cantidad:
                    venta.delete()  # Eliminar venta si no hay stock
                    return JsonResponse({
                        'success': False,
                        'message': f'Stock insuficiente para {item.producto.nombre}. Disponible: {item.producto.stock}'
                    }, status=400)
                
                # Crear detalle de venta
                detalle = DetalleVenta.objects.create(
                    venta=venta,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario
                )
                detalles_creados.append(detalle)
                
                # Actualizar stock del producto
                item.producto.stock -= item.cantidad
                item.producto.save()
            
            # Marcar venta como completada
            venta.estado = 'completada'
            venta.save()
            
            # Limpiar carrito
            items_carrito.delete()
            carrito.delete()
            
            # Registrar en bitácora
            from autenticacion_usuarios.models import Bitacora
            Bitacora.objects.create(
                id_usuario=usuario,
                accion='COMPRA_REALIZADA',
                modulo='VENTAS',
                descripcion=f'Cliente {usuario.nombre} realizó compra por ${total}',
                ip=self.get_client_ip(request)
            )
            
            # Respuesta exitosa
            return JsonResponse({
                'success': True,
                'message': 'Compra realizada exitosamente',
                'venta': {
                    'id': venta.id_venta,
                    'total': float(venta.total),
                    'fecha': venta.fecha_venta.isoformat(),
                    'estado': venta.estado,
                    'metodo_pago': venta.metodo_pago,
                    'direccion_entrega': venta.direccion_entrega,
                    'productos': len(detalles_creados)
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de datos inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
