from django.core.management.base import BaseCommand
from django.db import transaction
from autenticacion_usuarios.models import Usuario, Rol, Cliente

class Command(BaseCommand):
    help = 'Crea el usuario administrador inicial y datos básicos del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@smartsales365.com',
            help='Email del administrador'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Contraseña del administrador'
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Crear roles si no existen
                rol_admin, created = Rol.objects.get_or_create(
                    nombre='Administrador',
                    defaults={'nombre': 'Administrador'}
                )
                
                rol_cliente, created = Rol.objects.get_or_create(
                    nombre='Cliente',
                    defaults={'nombre': 'Cliente'}
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Roles creados/verificados: {rol_admin.nombre}, {rol_cliente.nombre}')
                )

                # Crear usuario administrador
                email = options['email']
                password = options['password']
                
                if Usuario.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'[WARN] El administrador con email {email} ya existe')
                    )
                    return

                admin_user = Usuario.objects.create(
                    nombre='Administrador',
                    apellido='Sistema',
                    email=email,
                    telefono='+591-000-0000',
                    id_rol=rol_admin,
                    estado=True
                )
                
                # Establecer contraseña
                admin_user.set_password(password)
                admin_user.save()

                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Usuario administrador creado:')
                )
                self.stdout.write(f'   Email: {email}')
                self.stdout.write(f'   Contraseña: {password}')
                self.stdout.write(f'   Nombre: {admin_user.nombre} {admin_user.apellido}')
                self.stdout.write(f'   Rol: {admin_user.id_rol.nombre}')

                # Crear algunos usuarios cliente de ejemplo
                clientes_ejemplo = [
                    {
                        'nombre': 'Juan',
                        'apellido': 'Pérez',
                        'email': 'juan.perez@email.com',
                        'telefono': '+591-123-4567',
                        'direccion': 'Av. Principal #123',
                        'ciudad': 'La Paz'
                    },
                    {
                        'nombre': 'María',
                        'apellido': 'González',
                        'email': 'maria.gonzalez@email.com',
                        'telefono': '+591-234-5678',
                        'direccion': 'Calle Libertad #456',
                        'ciudad': 'Santa Cruz'
                    }
                ]

                for cliente_data in clientes_ejemplo:
                    if not Usuario.objects.filter(email=cliente_data['email']).exists():
                        usuario_cliente = Usuario.objects.create(
                            nombre=cliente_data['nombre'],
                            apellido=cliente_data['apellido'],
                            email=cliente_data['email'],
                            telefono=cliente_data['telefono'],
                            id_rol=rol_cliente,
                            estado=True
                        )
                        usuario_cliente.set_password('cliente123')
                        usuario_cliente.save()

                        Cliente.objects.create(
                            id=usuario_cliente,
                            direccion=cliente_data['direccion'],
                            ciudad=cliente_data['ciudad']
                        )

                        self.stdout.write(
                            self.style.SUCCESS(f'[OK] Cliente creado: {cliente_data["nombre"]} {cliente_data["apellido"]}')
                        )

                self.stdout.write(
                    self.style.SUCCESS('\n[SUCCESS] Datos iniciales creados exitosamente!')
                )
                self.stdout.write('\nResumen:')
                self.stdout.write(f'   Administrador: {email} / {password}')
                self.stdout.write(f'   Clientes de prueba: cliente123')
                self.stdout.write(f'   Roles: Administrador, Cliente')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'[ERROR] Error creando datos iniciales: {str(e)}')
            )
            raise
