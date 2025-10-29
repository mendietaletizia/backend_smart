#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_smart.settings')
django.setup()

from productos.models import Categoria, Producto

# Crear categorías
cat_tech, _ = Categoria.objects.get_or_create(nombre='Tecnología')
cat_hogar, _ = Categoria.objects.get_or_create(nombre='Hogar')

# Crear productos
productos_data = [
    {
        'nombre': 'Laptop HP Pavilion',
        'descripcion': 'Laptop de 15 pulgadas con procesador Intel i5',
        'precio': 4299.00,
        'stock': 15,
        'imagen': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop',
        'categoria': cat_tech,
    },
    {
        'nombre': 'iPhone 14 Pro',
        'descripcion': 'Smartphone Apple con cámara Pro de 48MP',
        'precio': 8999.00,
        'stock': 8,
        'imagen': 'https://images.unsplash.com/photo-1592286927505-b0c6c9f0e6a7?w=400&h=300&fit=crop',
        'categoria': cat_tech,
    },
    {
        'nombre': 'Auriculares Sony WH-1000XM5',
        'descripcion': 'Auriculares inalámbricos con cancelación de ruido',
        'precio': 2499.00,
        'stock': 25,
        'imagen': 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&h=300&fit=crop',
        'categoria': cat_tech,
    },
]

for data in productos_data:
    obj, created = Producto.objects.get_or_create(
        nombre=data['nombre'],
        defaults=data
    )
    print(f"{'Creado' if created else 'Existente'}: {obj.nombre}")

print("Productos creados exitosamente!")
