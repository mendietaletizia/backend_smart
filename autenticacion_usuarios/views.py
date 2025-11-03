from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from .models import Usuario, Rol, Bitacora, Cliente

logger = logging.getLogger(__name__)

# ==========================================================
# CASO DE USO 1: INICIAR SESIÓN
# ==========================================================

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    """
    CU1: Iniciar Sesión
    Permite a usuarios (clientes y administradores) autenticarse en el sistema
    """
    
    def get(self, request):
        """Mostrar información del endpoint de login"""
        return JsonResponse({
            'endpoint': 'Login API',
            'method': 'POST',
            'description': 'Iniciar sesión en el sistema',
            'required_fields': ['email', 'contrasena'],
            'example': {
                'email': 'admin@tienda.com',
                'contrasena': 'admin123'
            },
            'note': 'Use POST method to login'
        })
    
    def post(self, request):
        try:
            # Obtener datos del request
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            contrasena = data.get('contrasena', '')
            
            # Validaciones básicas
            if not email or not contrasena:
                return JsonResponse({
                    'success': False,
                    'message': 'Email y contraseña son requeridos'
                }, status=400)
            
            # Buscar usuario por email
            try:
                usuario = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Credenciales inválidas'
                }, status=401)
            
            # Verificar si el usuario está activo
            if not usuario.is_active():
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario inactivo. Contacte al administrador.'
                }, status=401)
            
            # Verificar contraseña (hash o texto plano para entorno académico)
            if not (usuario.check_password(contrasena) or usuario.contrasena == contrasena):
                return JsonResponse({
                    'success': False,
                    'message': 'Credenciales inválidas'
                }, status=401)
            
            # Obtener IP del cliente
            ip_address = self.get_client_ip(request)
            
            # Registrar en bitácora
            Bitacora.objects.create(
                id_usuario=usuario,
                accion='INICIO_SESION',
                modulo='AUTENTICACION',
                descripcion=f'Usuario {usuario.nombre} inició sesión',
                ip=ip_address
            )
            
            # Crear sesión
            request.session['user_id'] = usuario.id
            request.session['user_email'] = usuario.email
            request.session['user_nombre'] = usuario.nombre
            request.session['user_rol'] = usuario.id_rol.nombre
            request.session['is_authenticated'] = True
            
            # Respuesta exitosa
            response_data = {
                'success': True,
                'message': 'Sesión iniciada correctamente',
                'user': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'email': usuario.email,
                    'rol': usuario.id_rol.nombre,
                    'telefono': usuario.telefono
                }
            }
            
            # Si es cliente, agregar información adicional
            if usuario.id_rol.nombre.lower() == 'cliente':
                try:
                    cliente = usuario.cliente
                    response_data['user']['direccion'] = cliente.direccion
                    response_data['user']['ciudad'] = cliente.ciudad
                except:
                    pass  # Si no tiene registro de cliente, no pasa nada
            
            return JsonResponse(response_data, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de datos inválido'
            }, status=400)
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=500)
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# ==========================================================
# CASO DE USO 2: CERRAR SESIÓN
# ==========================================================

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    """
    CU2: Cerrar Sesión
    Permite a usuarios autenticados cerrar su sesión en el sistema
    """
    
    def get(self, request):
        """Mostrar información del endpoint de logout"""
        return JsonResponse({
            'endpoint': 'Logout API',
            'method': 'POST',
            'description': 'Cerrar sesión en el sistema',
            'required_fields': [],
            'note': 'Use POST method to logout. Requires active session.'
        })
    
    def post(self, request):
        try:
            # Verificar si hay sesión activa
            if not request.session.get('is_authenticated'):
                return JsonResponse({
                    'success': False,
                    'message': 'No hay sesión activa'
                }, status=400)
            
            # Obtener información del usuario
            user_id = request.session.get('user_id')
            user_nombre = request.session.get('user_nombre', 'Usuario')
            
            # Obtener IP del cliente
            ip_address = self.get_client_ip(request)
            
            # Registrar en bitácora
            if user_id:
                try:
                    usuario = Usuario.objects.get(id=user_id)
                    Bitacora.objects.create(
                        id_usuario=usuario,
                        accion='CIERRE_SESION',
                        modulo='AUTENTICACION',
                        descripcion=f'Usuario {usuario.nombre} cerró sesión',
                        ip=ip_address
                    )
                except Usuario.DoesNotExist:
                    pass  # Si no existe el usuario, continuar con el logout
            
            # Limpiar sesión
            request.session.flush()
            
            return JsonResponse({
                'success': True,
                'message': 'Sesión cerrada correctamente'
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error en logout: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=500)
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# ==========================================================
# VISTA AUXILIAR: VERIFICAR SESIÓN
# ==========================================================

@method_decorator(csrf_exempt, name='dispatch')
class CheckSessionView(View):
    """
    Vista auxiliar para verificar si hay una sesión activa
    """
    
    def get(self, request):
        try:
            if request.session.get('is_authenticated'):
                user_id = request.session.get('user_id')
                try:
                    usuario = Usuario.objects.get(id=user_id)
                    return JsonResponse({
                        'success': True,
                        'authenticated': True,
                        'user': {
                            'id': usuario.id,
                            'nombre': usuario.nombre,
                            'apellido': usuario.apellido,
                            'email': usuario.email,
                            'rol': usuario.id_rol.nombre,
                            'telefono': usuario.telefono
                        }
                    })
                except Usuario.DoesNotExist:
                    request.session.flush()
                    return JsonResponse({
                        'success': True,
                        'authenticated': False
                    })
            else:
                return JsonResponse({
                    'success': True,
                    'authenticated': False
                })
        except Exception as e:
            logger.error(f"Error verificando sesión: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=500)


# ==========================================================
# CASO DE USO 3: REGISTRAR CUENTA DEL CLIENTE
# ==========================================================

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    """
    CU3: Registrar Cuenta del Cliente
    Permite a nuevos usuarios registrarse como clientes en el sistema
    """
    
    def get(self, request):
        """Mostrar información del endpoint de registro"""
        return JsonResponse({
            'endpoint': 'Register API',
            'method': 'POST',
            'description': 'Registrar nueva cuenta de cliente',
            'required_fields': ['nombre', 'apellido', 'email', 'contrasena', 'telefono'],
            'optional_fields': ['direccion', 'ciudad'],
            'example': {
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'email': 'juan@email.com',
                'contrasena': 'miPassword123',
                'telefono': '+1234567890',
                'direccion': 'Calle 123, #45',
                'ciudad': 'Ciudad'
            },
            'note': 'Use POST method to register. Email must be unique.'
        })
    
    def post(self, request):
        try:
            # Obtener datos del request
            data = json.loads(request.body)
            
            # Campos obligatorios
            nombre = data.get('nombre', '').strip()
            apellido = data.get('apellido', '').strip()
            email = data.get('email', '').strip().lower()
            contrasena = data.get('contrasena', '')
            telefono = data.get('telefono', '').strip()
            
            # Campos opcionales
            direccion = data.get('direccion', '').strip()
            ciudad = data.get('ciudad', '').strip()
            
            # Validaciones básicas
            if not nombre:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre es obligatorio'
                }, status=400)
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'El email es obligatorio'
                }, status=400)
            
            if not contrasena:
                return JsonResponse({
                    'success': False,
                    'message': 'La contraseña es obligatoria'
                }, status=400)
            
            if len(contrasena) < 6:
                return JsonResponse({
                    'success': False,
                    'message': 'La contraseña debe tener al menos 6 caracteres'
                }, status=400)
            
            # Validar formato de email básico
            if '@' not in email or '.' not in email:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de email inválido'
                }, status=400)
            
            # Verificar si el email ya existe
            if Usuario.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Este email ya está registrado'
                }, status=400)
            
            # Obtener o crear rol de Cliente
            try:
                rol_cliente = Rol.objects.get(nombre='Cliente')
            except Rol.DoesNotExist:
                rol_cliente = Rol.objects.create(nombre='Cliente')
            
            # Crear usuario
            usuario = Usuario.objects.create(
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=telefono,
                id_rol=rol_cliente,
                estado=True
            )
            
            # Encriptar contraseña
            usuario.set_password(contrasena)
            usuario.save()
            
            # Crear registro de cliente usando get_or_create para evitar duplicados
            cliente, created = Cliente.objects.get_or_create(
                id=usuario,
                defaults={
                    'direccion': direccion,
                    'ciudad': ciudad
                }
            )
            
            # Si ya existía, actualizar datos
            if not created:
                cliente.direccion = direccion
                cliente.ciudad = ciudad
                cliente.save()
            
            # Obtener IP del cliente
            ip_address = self.get_client_ip(request)
            
            # Registrar en bitácora
            Bitacora.objects.create(
                id_usuario=usuario,
                accion='REGISTRO_CLIENTE',
                modulo='AUTENTICACION',
                descripcion=f'Nuevo cliente registrado: {usuario.nombre} {usuario.apellido}',
                ip=ip_address
            )
            
            # Auto login: crear sesión para el nuevo usuario
            request.session['user_id'] = usuario.id
            request.session['user_email'] = usuario.email
            request.session['user_nombre'] = usuario.nombre
            request.session['user_rol'] = 'Cliente'
            request.session['is_authenticated'] = True

            # Respuesta exitosa
            return JsonResponse({
                'success': True,
                'message': 'Cuenta de cliente creada exitosamente',
                'user': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'email': usuario.email,
                    'telefono': usuario.telefono,
                    'direccion': cliente.direccion,
                    'ciudad': cliente.ciudad,
                    'rol': 'Cliente'
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de datos inválido'
            }, status=400)
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }, status=500)
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

