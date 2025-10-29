# Generated manually for ventas_carrito models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('productos', '0002_restructure_models'),
        ('autenticacion_usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id_carrito', models.AutoField(primary_key=True, serialize=False)),
                ('session_key', models.CharField(blank=True, max_length=40, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
                ('cliente', models.ForeignKey(blank=True, db_column='id_cliente', null=True, on_delete=django.db.models.deletion.CASCADE, to='autenticacion_usuarios.cliente')),
            ],
            options={
                'verbose_name': 'Carrito',
                'verbose_name_plural': 'Carritos',
                'db_table': 'carrito',
            },
        ),
        migrations.CreateModel(
            name='ItemCarrito',
            fields=[
                ('id_item', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField(default=1)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_agregado', models.DateTimeField(auto_now_add=True)),
                ('carrito', models.ForeignKey(db_column='id_carrito', on_delete=django.db.models.deletion.CASCADE, to='ventas_carrito.carrito')),
                ('producto', models.ForeignKey(db_column='id_producto', on_delete=django.db.models.deletion.CASCADE, to='productos.producto')),
            ],
            options={
                'verbose_name': 'Item del Carrito',
                'verbose_name_plural': 'Items del Carrito',
                'db_table': 'item_carrito',
            },
        ),
        migrations.AlterUniqueTogether(
            name='itemcarrito',
            unique_together={('carrito', 'producto')},
        ),
    ]
