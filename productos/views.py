from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import requests
import base64

from .models import Producto, Categoria, Marca, Proveedor, Stock


@method_decorator(csrf_exempt, name='dispatch')
class ProductoListView(View):
    """CU6: Listado público de productos"""
    def get(self, request):
        try:
            productos = Producto.objects.all().select_related('categoria', 'marca', 'proveedor')

            # Filtros CU7
            query = request.GET.get('q')
            categoria_nombre = request.GET.get('categoria')
            min_precio = request.GET.get('min')
            max_precio = request.GET.get('max')
            order_by = request.GET.get('order', 'nombre') # Default order

            if query:
                productos = productos.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))
            
            if categoria_nombre and categoria_nombre != 'Todos':
                productos = productos.filter(categoria__nombre__iexact=categoria_nombre)
            
            if min_precio:
                productos = productos.filter(precio__gte=min_precio)
            
            if max_precio:
                productos = productos.filter(precio__lte=max_precio)
            
            # Ordenamiento
            if order_by in ['nombre', 'precio', '-precio']:
                productos = productos.order_by(order_by)
            else:
                productos = productos.order_by('nombre') # Default fallback

            # Paginación (simple, se puede mejorar con Django Paginator)
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            start = (page - 1) * page_size
            end = start + page_size

            total_items = productos.count()
            productos = productos[start:end]

            data = []
            for p in productos:
                # Obtener stock actual
                stock_obj = Stock.objects.filter(producto=p).first()
                stock_cantidad = stock_obj.cantidad if stock_obj else 0
                
                data.append({
                    'id': p.id,
                    'nombre': p.nombre,
                    'descripcion': p.descripcion,
                    'precio': float(p.precio),
                    'stock': stock_cantidad,
                    'imagen': p.imagen,
                    'categoria': p.categoria.nombre if p.categoria else None,
                    'marca': p.marca.nombre if p.marca else None,
                    'proveedor': p.proveedor.nombre if p.proveedor else None,
                    'estado': True,
                })
            
            return JsonResponse({
                'success': True,
                'items': data,
                'total': total_items,
                'page': page,
                'page_size': page_size,
            }, status=200)

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProductoAdminView(View):
    """CU4: Gestión administrativa de productos"""
    
    def get(self, request):
        """Listar todos los productos para administración"""
        try:
            productos = Producto.objects.all().select_related('categoria', 'marca', 'proveedor')
            
            # Filtros administrativos
            query = request.GET.get('q')
            categoria_nombre = request.GET.get('categoria')
            order_by = request.GET.get('order', 'nombre')

            if query:
                productos = productos.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))
            
            if categoria_nombre and categoria_nombre != 'Todos':
                productos = productos.filter(categoria__nombre__iexact=categoria_nombre)
            
            # Ordenamiento
            if order_by in ['nombre', 'precio', '-precio']:
                productos = productos.order_by(order_by)
            else:
                productos = productos.order_by('nombre')

            # Paginación
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 100))
            start = (page - 1) * page_size
            end = start + page_size

            total_items = productos.count()
            productos = productos[start:end]

            data = []
            for p in productos:
                # Obtener stock actual
                stock_obj = Stock.objects.filter(producto=p).first()
                stock_cantidad = stock_obj.cantidad if stock_obj else 0
                
                data.append({
                    'id': p.id,
                    'nombre': p.nombre,
                    'descripcion': p.descripcion,
                    'precio': float(p.precio),
                    'stock': stock_cantidad,
                    'imagen': p.imagen,
                    'categoria': p.categoria.nombre if p.categoria else None,
                    'marca': p.marca.nombre if p.marca else None,
                    'proveedor': p.proveedor.nombre if p.proveedor else None,
                    'estado': True,
                })
            
            return JsonResponse({
                'success': True,
                'items': data,
                'total': total_items,
                'page': page,
                'page_size': page_size,
            }, status=200)

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def post(self, request):
        """Crear nuevo producto"""
        try:
            data = json.loads(request.body)
            
            # Validaciones básicas
            if not data.get('nombre'):
                return JsonResponse({'success': False, 'message': 'El nombre es obligatorio'}, status=400)
            
            if not data.get('precio'):
                return JsonResponse({'success': False, 'message': 'El precio es obligatorio'}, status=400)

            # Obtener o crear categoría
            categoria = None
            if data.get('categoria'):
                categoria, _ = Categoria.objects.get_or_create(nombre=data['categoria'])
            
            # Obtener o crear marca
            marca = None
            if data.get('marca'):
                marca, _ = Marca.objects.get_or_create(nombre=data['marca'])
            
            # Obtener o crear proveedor
            proveedor = None
            if data.get('proveedor'):
                proveedor, _ = Proveedor.objects.get_or_create(nombre=data['proveedor'])

            # Crear producto
            producto = Producto.objects.create(
                nombre=data['nombre'],
                descripcion=data.get('descripcion', ''),
                precio=data['precio'],
                imagen=data.get('imagen', ''),
                categoria=categoria,
                marca=marca,
                proveedor=proveedor
            )

            # Crear stock inicial
            stock_cantidad = data.get('stock', 0)
            if stock_cantidad > 0:
                Stock.objects.create(
                    producto=producto,
                    cantidad=stock_cantidad
                )

            return JsonResponse({
                'success': True,
                'message': 'Producto creado exitosamente',
                'id': producto.id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def put(self, request):
        """Actualizar producto existente"""
        try:
            data = json.loads(request.body)
            producto_id = data.get('id')
            
            if not producto_id:
                return JsonResponse({'success': False, 'message': 'ID de producto requerido'}, status=400)

            try:
                producto = Producto.objects.get(id=producto_id)
            except Producto.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Producto no encontrado'}, status=404)

            # Actualizar campos
            if 'nombre' in data:
                producto.nombre = data['nombre']
            if 'descripcion' in data:
                producto.descripcion = data['descripcion']
            if 'precio' in data:
                producto.precio = data['precio']
            if 'imagen' in data:
                producto.imagen = data['imagen']

            # Actualizar relaciones
            if 'categoria' in data:
                if data['categoria']:
                    categoria, _ = Categoria.objects.get_or_create(nombre=data['categoria'])
                    producto.categoria = categoria
                else:
                    producto.categoria = None
            
            if 'marca' in data:
                if data['marca']:
                    marca, _ = Marca.objects.get_or_create(nombre=data['marca'])
                    producto.marca = marca
                else:
                    producto.marca = None
            
            if 'proveedor' in data:
                if data['proveedor']:
                    proveedor, _ = Proveedor.objects.get_or_create(nombre=data['proveedor'])
                    producto.proveedor = proveedor
                else:
                    producto.proveedor = None

            producto.save()

            # Actualizar stock
            if 'stock' in data:
                stock_obj, created = Stock.objects.get_or_create(producto=producto)
                stock_obj.cantidad = data['stock']
                stock_obj.save()

            return JsonResponse({
                'success': True,
                'message': 'Producto actualizado exitosamente'
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def delete(self, request):
        """Eliminar producto"""
        try:
            producto_id = request.GET.get('id')
            
            if not producto_id:
                return JsonResponse({'success': False, 'message': 'ID de producto requerido'}, status=400)

            try:
                producto = Producto.objects.get(id=producto_id)
            except Producto.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Producto no encontrado'}, status=404)

            # Eliminar stock asociado
            Stock.objects.filter(producto=producto).delete()
            
            # Eliminar producto
            producto.delete()

            return JsonResponse({
                'success': True,
                'message': 'Producto eliminado exitosamente'
            }, status=200)

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UploadImageView(View):
    """Nueva funcionalidad: Subir imágenes a ImgBB"""
    
    def post(self, request):
        """Subir imagen a ImgBB y devolver URL"""
        try:
            # Obtener archivo del frontend
            file = request.FILES.get('image')
            if not file:
                return JsonResponse({
                    'success': False, 
                    'message': 'No se envió imagen'
                }, status=400)
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if file.content_type not in allowed_types:
                return JsonResponse({
                    'success': False, 
                    'message': 'Tipo de archivo no válido. Solo se permiten: JPEG, PNG, GIF, WebP'
                }, status=400)
            
            # Validar tamaño (32MB máximo para ImgBB gratuito)
            if file.size > 32 * 1024 * 1024:
                return JsonResponse({
                    'success': False, 
                    'message': 'Archivo demasiado grande. Máximo 32MB'
                }, status=400)
            
            # Convertir a base64
            file_data = file.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
            
            # Subir a ImgBB
            url = 'https://api.imgbb.com/1/upload'
            data = {
                'key': settings.API_KEY_IMGBB,
                'image': base64_data
            }
            
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if result.get('success'):
                image_url = result['data']['url']
                return JsonResponse({
                    'success': True,
                    'image_url': image_url,
                    'message': 'Imagen subida exitosamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error al subir imagen a ImgBB'
                }, status=400)
                
        except requests.exceptions.Timeout:
            return JsonResponse({
                'success': False,
                'message': 'Timeout al subir imagen'
            }, status=500)
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'success': False,
                'message': f'Error de conexión: {str(e)}'
            }, status=500)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)

