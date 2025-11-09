# Generated manually for CU14-CU20
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
            name='ModeloIA',
            fields=[
                ('id_modelo', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('algoritmo', models.CharField(max_length=50)),
                ('fecha_entrenamiento', models.DateTimeField(auto_now_add=True)),
                ('r2_score', models.FloatField(blank=True, null=True)),
                ('rmse', models.FloatField(blank=True, null=True)),
                ('ruta_modelo', models.CharField(blank=True, max_length=500, null=True)),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('entrenando', 'Entrenando'), ('retirado', 'Retirado'), ('error', 'Error')], default='activo', max_length=20)),
                ('version', models.CharField(default='1.0', max_length=20)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'modelo_ia',
                'verbose_name': 'Modelo de IA',
                'verbose_name_plural': 'Modelos de IA',
                'ordering': ['-fecha_entrenamiento'],
            },
        ),
        migrations.CreateModel(
            name='PrediccionVenta',
            fields=[
                ('id_prediccion', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_prediccion', models.DateField()),
                ('valor_predicho', models.DecimalField(decimal_places=2, max_digits=10)),
                ('modelo_version', models.CharField(default='1.0', max_length=20)),
                ('fecha_ejecucion', models.DateTimeField(auto_now_add=True)),
                ('confianza', models.FloatField(default=0.0)),
                ('categoria', models.ForeignKey(blank=True, db_column='id_categoria', null=True, on_delete=django.db.models.deletion.SET_NULL, to='productos.categoria')),
                ('modelo', models.ForeignKey(blank=True, db_column='id_modelo', null=True, on_delete=django.db.models.deletion.SET_NULL, to='reportes_dinamicos.modeloia')),
            ],
            options={
                'db_table': 'prediccion_venta',
                'verbose_name': 'Predicción de Venta',
                'verbose_name_plural': 'Predicciones de Venta',
                'ordering': ['-fecha_ejecucion'],
            },
        ),
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id_reporte', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=200)),
                ('tipo', models.CharField(choices=[('ventas', 'Ventas'), ('productos', 'Productos'), ('clientes', 'Clientes'), ('inventario', 'Inventario'), ('financiero', 'Financiero'), ('general', 'General')], max_length=50)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('parametros', models.JSONField(blank=True, default=dict)),
                ('prompt', models.TextField(blank=True, null=True)),
                ('formato', models.CharField(choices=[('pantalla', 'Pantalla'), ('pdf', 'PDF'), ('excel', 'Excel'), ('json', 'JSON')], default='pantalla', max_length=20)),
                ('origen_comando', models.CharField(choices=[('texto', 'Texto'), ('voz', 'Voz'), ('manual', 'Manual')], default='manual', max_length=20)),
                ('fecha_generacion', models.DateTimeField(auto_now_add=True)),
                ('ruta_archivo', models.CharField(blank=True, max_length=500, null=True)),
                ('datos', models.JSONField(blank=True, default=dict)),
                ('filtros_aplicados', models.JSONField(blank=True, default=dict)),
                ('estado', models.CharField(default='completado', max_length=20)),
                ('id_usuario', models.ForeignKey(blank=True, db_column='id_usuario', null=True, on_delete=django.db.models.deletion.SET_NULL, to='autenticacion_usuarios.usuario')),
            ],
            options={
                'db_table': 'reporte',
                'verbose_name': 'Reporte',
                'verbose_name_plural': 'Reportes',
                'ordering': ['-fecha_generacion'],
            },
        ),
    ]


