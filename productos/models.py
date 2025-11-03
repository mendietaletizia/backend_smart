from django.db import models


class Marca(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'marca'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    # PK real en DB es 'id'
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    # La columna con datos en DB es 'precio_unitario'
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, db_column='precio_unitario')
    # Columna existente para precio de compra
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, db_column='precio_unitario_compra')
    imagen = models.URLField(max_length=500, blank=True, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_marca')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_categoria')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_proveedor')

    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Stock(models.Model):
    id_stock = models.AutoField(primary_key=True)
    cantidad = models.IntegerField(default=0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')

    class Meta:
        db_table = 'stock'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'

    def __str__(self):
        return f"Stock {self.producto.nombre}: {self.cantidad}"


class Medidas(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_medida = models.CharField(max_length=50)  # peso, volumen, dimensiones, etc.
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    unidad = models.CharField(max_length=20)  # kg, cm, litros, etc.
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')

    class Meta:
        db_table = 'medidas'
        verbose_name = 'Medida'
        verbose_name_plural = 'Medidas'

    def __str__(self):
        return f"{self.producto.nombre}: {self.valor} {self.unidad}"