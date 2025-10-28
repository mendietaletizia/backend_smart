from django.core.management.base import BaseCommand
from autenticacion_usuarios.models import Rol, Usuario

class Command(BaseCommand):
    help = 'Crear datos iniciales para el sistema de autenticación'

    def handle(self, *args, **options):
        # Crear roles básicos
        roles_data = [
            {'nombre': 'Administrador'},
            {'nombre': 'Cliente'},
        ]
        
        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults=rol_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Rol creado: {rol.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Rol ya existe: {rol.nombre}')
                )
        
        # Crear usuario administrador por defecto
        admin_rol = Rol.objects.get(nombre='Administrador')
        admin_user, created = Usuario.objects.get_or_create(
            email='admin@tienda.com',
            defaults={
                'nombre': 'Administrador',
                'apellido': 'Sistema',
                'id_rol': admin_rol,
                'estado': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Usuario administrador creado: admin@tienda.com / admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Usuario administrador ya existe')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Datos iniciales creados exitosamente')
        )
