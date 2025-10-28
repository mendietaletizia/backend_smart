# API de Autenticación - Casos de Uso CU1 y CU2

## Descripción
Este documento describe los endpoints implementados para los casos de uso de autenticación en la tienda virtual.

## Endpoints Disponibles

### 1. CU1: Iniciar Sesión
**Endpoint:** `POST /api/auth/login/`

**Descripción:** Permite a usuarios (clientes y administradores) autenticarse en el sistema.

**Parámetros de entrada:**
```json
{
    "email": "usuario@ejemplo.com",
    "contrasena": "password123"
}
```

**Respuesta exitosa (200):**
```json
{
    "success": true,
    "message": "Sesión iniciada correctamente",
    "user": {
        "id": 1,
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "usuario@ejemplo.com",
        "rol": "Cliente",
        "telefono": "123456789",
        "direccion": "Calle 123",
        "ciudad": "La Paz"
    }
}
```

**Respuestas de error:**
- **400:** Datos faltantes o formato inválido
- **401:** Credenciales inválidas o usuario inactivo
- **500:** Error interno del servidor

### 2. CU2: Cerrar Sesión
**Endpoint:** `POST /api/auth/logout/`

**Descripción:** Permite a usuarios autenticados cerrar su sesión en el sistema.

**Parámetros de entrada:** Ninguno (usa la sesión actual)

**Respuesta exitosa (200):**
```json
{
    "success": true,
    "message": "Sesión cerrada correctamente"
}
```

**Respuestas de error:**
- **400:** No hay sesión activa
- **500:** Error interno del servidor

### 3. Verificar Sesión
**Endpoint:** `GET /api/auth/check-session/`

**Descripción:** Verifica si hay una sesión activa y devuelve información del usuario.

**Respuesta con sesión activa (200):**
```json
{
    "success": true,
    "authenticated": true,
    "user": {
        "id": 1,
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "usuario@ejemplo.com",
        "rol": "Cliente",
        "telefono": "123456789"
    }
}
```

**Respuesta sin sesión activa (200):**
```json
{
    "success": true,
    "authenticated": false
}
```

## Características Implementadas

### Seguridad
- Encriptación de contraseñas usando Django's password hashers
- Validación de usuarios activos
- Registro de acciones en bitácora con IP
- Manejo de sesiones seguro

### Auditoría
- Registro automático de inicio y cierre de sesión
- Captura de IP del cliente
- Registro en tabla `bitacora` para trazabilidad

### Roles de Usuario
- **Administrador:** Acceso completo al sistema
- **Cliente:** Acceso limitado a funcionalidades de cliente

## Datos de Prueba

### Usuario Administrador
- **Email:** admin@tienda.com
- **Contraseña:** admin123
- **Rol:** Administrador

### Crear Datos Iniciales
Para crear los roles y usuario administrador por defecto, ejecutar:
```bash
python manage.py crear_datos_iniciales
```

## Ejemplos de Uso

### JavaScript (Frontend)
```javascript
// Iniciar sesión
const loginData = {
    email: 'usuario@ejemplo.com',
    contrasena: 'password123'
};

fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(loginData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Sesión iniciada:', data.user);
        // Redirigir según el rol
        if (data.user.rol === 'Administrador') {
            window.location.href = '/admin-dashboard';
        } else {
            window.location.href = '/cliente-dashboard';
        }
    } else {
        console.error('Error:', data.message);
    }
});

// Cerrar sesión
fetch('/api/auth/logout/', {
    method: 'POST',
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Sesión cerrada');
        window.location.href = '/login';
    }
});

// Verificar sesión
fetch('/api/auth/check-session/')
.then(response => response.json())
.then(data => {
    if (data.authenticated) {
        console.log('Usuario autenticado:', data.user);
    } else {
        console.log('No hay sesión activa');
    }
});
```

### Python (Requests)
```python
import requests

# Iniciar sesión
login_data = {
    'email': 'usuario@ejemplo.com',
    'contrasena': 'password123'
}

response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
if response.status_code == 200:
    data = response.json()
    print('Sesión iniciada:', data['user'])
else:
    print('Error:', response.json()['message'])

# Cerrar sesión
response = requests.post('http://localhost:8000/api/auth/logout/')
if response.status_code == 200:
    print('Sesión cerrada')
```

## Notas Importantes

1. **Sesiones:** El sistema usa sesiones de Django para mantener el estado de autenticación
2. **CORS:** Configurado para permitir conexiones desde cualquier origen (desarrollo)
3. **CSRF:** Deshabilitado para facilitar pruebas con APIs
4. **Logging:** Todas las acciones se registran en la tabla `bitacora`
5. **Roles:** El sistema distingue entre Administrador y Cliente para diferentes funcionalidades
