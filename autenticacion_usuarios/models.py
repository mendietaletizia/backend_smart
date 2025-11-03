from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# ==========================================================
# MODELOS DE AUTENTICACIÓN
# ==========================================================

class Rol(models.Model):
    """Modelo para roles de usuario (Cliente, Administrador)"""
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    """Modelo principal de usuario"""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    contrasena = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    id_rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column='id_rol')
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido or ''}".strip()
    
    def set_password(self, raw_password):
        """Encriptar contraseña"""
        self.contrasena = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verificar contraseña"""
        return check_password(raw_password, self.contrasena)
    
    def is_active(self):
        """Verificar si el usuario está activo"""
        return self.estado
    
    @property
    def is_authenticated(self):
        """Para compatibilidad con Django auth"""
        return True
    
    @property
    def is_anonymous(self):
        """Para compatibilidad con Django auth"""
        return False

class Cliente(models.Model):
    """Modelo de cliente que hereda de Usuario"""
    id = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, db_column='id')
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return f"Cliente: {self.id.nombre} {self.id.apellido or ''}".strip()

class Bitacora(models.Model):
    """Modelo para registrar acciones de usuario"""
    id_bitacora = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=50, blank=True, null=True)
    accion = models.CharField(max_length=100)
    modulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    
    class Meta:
        db_table = 'bitacora'
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.accion} - {self.id_usuario.nombre} ({self.fecha})"

class Notificacion(models.Model):
    """Modelo para notificaciones de usuario"""
    id_notificacion = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50)
    prioridad = models.CharField(max_length=20, default='normal')
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    
    class Meta:
        db_table = 'notificacion'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"{self.titulo} - {self.id_usuario.nombre}"
