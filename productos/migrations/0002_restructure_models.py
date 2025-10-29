# Generated manually to handle model restructuring

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        # Create Marca model
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id_marca', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Marca',
                'verbose_name_plural': 'Marcas',
                'db_table': 'marca',
            },
        ),
        
        # Create Proveedor model
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id_proveedor', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=200)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('direccion', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Proveedor',
                'verbose_name_plural': 'Proveedores',
                'db_table': 'proveedor',
            },
        ),
        
        # Create Stock model
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id_stock', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField(default=0)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Stock',
                'verbose_name_plural': 'Stocks',
                'db_table': 'stock',
            },
        ),
        
        # Create Medidas model
        migrations.CreateModel(
            name='Medidas',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tipo_medida', models.CharField(max_length=50)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unidad', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'Medida',
                'verbose_name_plural': 'Medidas',
                'db_table': 'medidas',
            },
        ),
        
        # Add new fields to Producto
        migrations.AddField(
            model_name='producto',
            name='marca',
            field=models.ForeignKey(blank=True, db_column='id_marca', null=True, on_delete=django.db.models.deletion.SET_NULL, to='productos.marca'),
        ),
        migrations.AddField(
            model_name='producto',
            name='proveedor',
            field=models.ForeignKey(blank=True, db_column='id_proveedor', null=True, on_delete=django.db.models.deletion.SET_NULL, to='productos.proveedor'),
        ),
        
        # Rename precio to precio_u_c
        migrations.RenameField(
            model_name='producto',
            old_name='precio',
            new_name='precio_u_c',
        ),
        
        # Rename id to id_producto
        migrations.RenameField(
            model_name='producto',
            old_name='id',
            new_name='id_producto',
        ),
        
        # Add foreign key to Stock
        migrations.AddField(
            model_name='stock',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.producto', db_column='id_producto'),
        ),
        
        # Add foreign key to Medidas
        migrations.AddField(
            model_name='medidas',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.producto', db_column='id_producto'),
        ),
    ]
