from django.core.management.base import BaseCommand
from productos.models import Categoria, Producto, Marca, Proveedor, Stock


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para productos (CU6)'

    def handle(self, *args, **options):
        # Crear marcas
        marca_hp, _ = Marca.objects.get_or_create(nombre='HP')
        marca_apple, _ = Marca.objects.get_or_create(nombre='Apple')
        marca_sony, _ = Marca.objects.get_or_create(nombre='Sony')
        marca_samsung, _ = Marca.objects.get_or_create(nombre='Samsung')
        marca_nespresso, _ = Marca.objects.get_or_create(nombre='Nespresso')

        # Crear proveedores
        proveedor_tech, _ = Proveedor.objects.get_or_create(
            nombre='TechSupply Corp',
            defaults={
                'telefono': '+1-555-0123',
                'email': 'contact@techsupply.com',
                'direccion': '123 Tech Street, Silicon Valley'
            }
        )
        proveedor_hogar, _ = Proveedor.objects.get_or_create(
            nombre='HomeGoods Inc',
            defaults={
                'telefono': '+1-555-0456',
                'email': 'sales@homegoods.com',
                'direccion': '456 Home Avenue, Commerce City'
            }
        )

        # Crear categorías
        cat_tech, _ = Categoria.objects.get_or_create(nombre='Tecnología')
        cat_hogar, _ = Categoria.objects.get_or_create(nombre='Hogar')
        cat_deportes, _ = Categoria.objects.get_or_create(nombre='Deportes')

        # Productos de ejemplo
        items = [
            {
                'nombre': 'Laptop HP Pavilion',
                'descripcion': 'Laptop de 15 pulgadas con procesador Intel i5',
                'precio': 4299.00,
                'precio_compra': 3200.00,
                'stock': 15,
                'imagen': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop',
                'categoria': cat_tech,
                'marca': marca_hp,
                'proveedor': proveedor_tech,
            },
            {
                'nombre': 'iPhone 14 Pro',
                'descripcion': 'Smartphone Apple con cámara Pro de 48MP',
                'precio': 8999.00,
                'precio_compra': 6500.00,
                'stock': 8,
                'imagen': 'https://images.unsplash.com/photo-1592286927505-b0c6c9f0e6a7?w=400&h=300&fit=crop',
                'categoria': cat_tech,
                'marca': marca_apple,
                'proveedor': proveedor_tech,
            },
            {
                'nombre': 'Auriculares Sony WH-1000XM5',
                'descripcion': 'Auriculares inalámbricos con cancelación de ruido',
                'precio': 2499.00,
                'precio_compra': 1800.00,
                'stock': 25,
                'imagen': 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&h=300&fit=crop',
                'categoria': cat_tech,
                'marca': marca_sony,
                'proveedor': proveedor_tech,
            },
            {
                'nombre': 'Smart TV Samsung 55"',
                'descripcion': 'Televisor 4K con tecnología QLED',
                'precio': 5799.00,
                'precio_compra': 4200.00,
                'stock': 12,
                'imagen': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400&h=300&fit=crop',
                'categoria': cat_tech,
                'marca': marca_samsung,
                'proveedor': proveedor_tech,
            },
            {
                'nombre': 'Cafetera Nespresso',
                'descripcion': 'Máquina de café automática con cápsulas',
                'precio': 1899.00,
                'precio_compra': 1200.00,
                'stock': 30,
                'imagen': 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=400&h=300&fit=crop',
                'categoria': cat_hogar,
                'marca': marca_nespresso,
                'proveedor': proveedor_hogar,
            },
            {
                'nombre': 'Tablet iPad Air',
                'descripcion': 'Tablet Apple con pantalla Liquid Retina de 10.9"',
                'precio': 6499.00,
                'precio_compra': 4800.00,
                'stock': 18,
                'imagen': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=300&fit=crop',
                'categoria': cat_tech,
                'marca': marca_apple,
                'proveedor': proveedor_tech,
            },
        ]

        for data in items:
            stock_cantidad = data.pop('stock')  # Remover stock de los datos del producto
            
            obj, created = Producto.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            
            # Crear stock para el producto
            if created or not Stock.objects.filter(producto=obj).exists():
                Stock.objects.create(
                    producto=obj,
                    cantidad=stock_cantidad
                )
            
            self.stdout.write(self.style.SUCCESS(f"{'Creado' if created else 'Existente'}: {obj.nombre}"))

        self.stdout.write(self.style.SUCCESS('Productos de ejemplo listos'))


