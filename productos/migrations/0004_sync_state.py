# Migración para sincronizar el estado de Django con la BD real
# La migración 0003 ya hizo todos los cambios en la BD de forma segura
# Esta migración solo sincroniza el estado interno de Django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0003_rename_id_producto_producto_id_and_more'),
    ]

    operations = [
        # Esta migración no hace cambios en la BD
        # Solo sincroniza el estado de Django para que coincida con la BD real
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # No hacer nada en la BD - ya está correcta
            ],
            state_operations=[
                # Sincronizar el estado: el campo se llama 'id', no 'id_producto'
                migrations.RenameField(
                    model_name='producto',
                    old_name='id_producto',
                    new_name='id',
                ),
                # Eliminar campos que ya no existen en el modelo
                migrations.RemoveField(
                    model_name='producto',
                    name='estado',
                ),
                migrations.RemoveField(
                    model_name='producto',
                    name='fecha_actualizacion',
                ),
                migrations.RemoveField(
                    model_name='producto',
                    name='fecha_creacion',
                ),
                migrations.RemoveField(
                    model_name='producto',
                    name='precio_u_c',
                ),
                migrations.RemoveField(
                    model_name='producto',
                    name='stock',
                ),
            ],
        ),
    ]

