from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_restructure_models'),
        ('autenticacion_usuarios', '0001_initial'),
        ('ventas_carrito', '0003_auto_20251028_1732'),
    ]

    operations = [
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id_venta', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_venta', models.DateTimeField(auto_now_add=True)),
                ('total', models.DecimalField(max_digits=10, decimal_places=2)),
                ('estado', models.CharField(max_length=20, default='pendiente')),
                ('metodo_pago', models.CharField(max_length=50, default='efectivo')),
                ('direccion_entrega', models.CharField(max_length=255, blank=True, null=True)),
                ('notas', models.TextField(blank=True, null=True)),
                ('cliente', models.ForeignKey(db_column='id_cliente', on_delete=django.db.models.deletion.CASCADE, to='autenticacion_usuarios.cliente')),
            ],
            options={
                'db_table': 'venta',
                'verbose_name': 'Venta',
                'verbose_name_plural': 'Ventas',
                'ordering': ['-fecha_venta'],
            },
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id_detalle', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.PositiveIntegerField()),
                ('precio_unitario', models.DecimalField(max_digits=10, decimal_places=2)),
                ('subtotal', models.DecimalField(max_digits=10, decimal_places=2)),
                # Usar entero para evitar conflicto de PK entre 'id' vs 'id_producto' en tabla producto.
                ('producto_id', models.IntegerField(db_column='id_producto')),
                ('venta', models.ForeignKey(db_column='venta_id', on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='ventas_carrito.venta')),
            ],
            options={
                'db_table': 'detalle_venta',
                'verbose_name': 'Detalle de Venta',
                'verbose_name_plural': 'Detalles de Venta',
            },
        ),
    ]


