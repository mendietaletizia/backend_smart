from django.db import models
from django.conf import settings
from productos.models import Producto
from autenticacion_usuarios.models import Cliente

class Carrito(models.Model):
    id_carrito = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True, db_column='id_cliente')
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'carrito'
        verbose_name = 'Carrito de Compras'
        verbose_name_plural = 'Carritos de Compras'

    def __str__(self):
        if self.cliente:
            return f"Carrito de {self.cliente.id.nombre}"
        return f"Carrito (sesión: {self.session_key[:5]}...)"

    def get_total_items(self):
        return self.items.aggregate(total_cantidad=models.Sum('cantidad'))['total_cantidad'] or 0

    def get_total_precio(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        return total

class ItemCarrito(models.Model):
    id_item = models.AutoField(primary_key=True)
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE, db_column='id_carrito')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_adicion = models.DateTimeField(auto_now_add=True, db_column='fecha_agregado')

    class Meta:
        db_table = 'item_carrito'
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
        unique_together = ('carrito', 'producto') # Un producto por carrito

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Carrito {self.carrito.id_carrito}"

    def get_subtotal(self):
        return self.cantidad * self.precio_unitario

class Venta(models.Model):
    """Modelo para registrar ventas"""
    id_venta = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='pendiente')  # pendiente, completada, cancelada
    metodo_pago = models.CharField(max_length=50, default='efectivo')  # efectivo, tarjeta, transferencia
    direccion_entrega = models.CharField(max_length=255, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'venta'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta #{self.id_venta} - {self.cliente.id.nombre} - ${self.total}"

class DetalleVenta(models.Model):
    """Modelo para detalles de venta"""
    id_detalle = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE, db_column='venta_id')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'detalle_venta'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} - ${self.subtotal}"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)