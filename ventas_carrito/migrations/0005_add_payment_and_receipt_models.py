# Generated manually for CU11, CU12, CU13
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_restructure_models'),
        ('autenticacion_usuarios', '0001_initial'),
        ('ventas_carrito', '0004_create_sales_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetodoPago',
            fields=[
                ('id_mp', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'db_table': 'metodo_de_pago',
                'verbose_name': 'Método de Pago',
                'verbose_name_plural': 'Métodos de Pago',
            },
        ),
        migrations.CreateModel(
            name='PagoOnline',
            fields=[
                ('id_pago', models.AutoField(primary_key=True, serialize=False)),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado', models.CharField(default='pendiente', max_length=20)),
                ('referencia', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('datos_tarjeta_hash', models.CharField(blank=True, max_length=255, null=True)),
                ('metodo_pago', models.ForeignKey(blank=True, db_column='id_mp', null=True, on_delete=django.db.models.deletion.SET_NULL, to='ventas_carrito.metodopago')),
                ('venta', models.OneToOneField(db_column='venta_id', on_delete=django.db.models.deletion.CASCADE, related_name='pago_online', to='ventas_carrito.venta')),
            ],
            options={
                'db_table': 'pago_online',
                'verbose_name': 'Pago Online',
                'verbose_name_plural': 'Pagos Online',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Comprobante',
            fields=[
                ('id_comprobante', models.AutoField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(choices=[('factura', 'Factura'), ('recibo', 'Recibo'), ('nota_credito', 'Nota de Crédito'), ('nota_debito', 'Nota de Débito')], default='factura', max_length=20)),
                ('nit', models.CharField(blank=True, max_length=20, null=True)),
                ('nro', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('fecha_emision', models.DateTimeField(auto_now_add=True)),
                ('pdf_ruta', models.CharField(blank=True, max_length=500, null=True)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('generado', 'Generado'), ('anulado', 'Anulado')], default='pendiente', max_length=20)),
                ('total_factura', models.DecimalField(decimal_places=2, max_digits=10)),
                ('venta', models.OneToOneField(db_column='venta_id', on_delete=django.db.models.deletion.CASCADE, related_name='comprobante', to='ventas_carrito.venta')),
            ],
            options={
                'db_table': 'comprobante',
                'verbose_name': 'Comprobante',
                'verbose_name_plural': 'Comprobantes',
                'ordering': ['-fecha_emision'],
            },
        ),
        migrations.CreateModel(
            name='VentaHistorico',
            fields=[
                ('id_his', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateField()),
                ('cantidad_total', models.IntegerField(default=0)),
                ('monto_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('ventas_count', models.IntegerField(default=0)),
                ('categoria', models.ForeignKey(blank=True, db_column='id_categoria', null=True, on_delete=django.db.models.deletion.SET_NULL, to='productos.categoria')),
            ],
            options={
                'db_table': 'venta_historico',
                'verbose_name': 'Historial de Venta',
                'verbose_name_plural': 'Historial de Ventas',
                'ordering': ['-fecha'],
                'unique_together': {('fecha', 'categoria')},
            },
        ),
    ]


