from django.contrib import admin
from .models import Rol, Usuario, Cliente, Bitacora, Notificacion

# ==========================================================
# ADMINISTRACIÓN DE MODELOS DE AUTENTICACIÓN
# ==========================================================

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id_rol', 'nombre')
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'email', 'id_rol', 'estado')
    list_filter = ('estado', 'id_rol')
    search_fields = ('nombre', 'apellido', 'email')
    ordering = ('nombre',)
    readonly_fields = ('id',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'email', 'telefono')
        }),
        ('Autenticación', {
            'fields': ('contrasena', 'id_rol', 'estado')
        }),
    )

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_nombre', 'get_email', 'direccion', 'ciudad')
    search_fields = ('id__nombre', 'id__apellido', 'id__email', 'direccion', 'ciudad')
    ordering = ('id__nombre',)
    
    def get_nombre(self, obj):
        return f"{obj.id.nombre} {obj.id.apellido or ''}".strip()
    get_nombre.short_description = 'Nombre'
    
    def get_email(self, obj):
        return obj.id.email
    get_email.short_description = 'Email'

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('id_bitacora', 'id_usuario', 'accion', 'modulo', 'fecha', 'ip')
    list_filter = ('accion', 'modulo', 'fecha')
    search_fields = ('id_usuario__nombre', 'accion', 'modulo', 'descripcion')
    ordering = ('-fecha',)
    readonly_fields = ('id_bitacora', 'fecha')
    
    fieldsets = (
        ('Información de la Acción', {
            'fields': ('id_usuario', 'accion', 'modulo', 'descripcion')
        }),
        ('Detalles Técnicos', {
            'fields': ('fecha', 'ip')
        }),
    )

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id_notificacion', 'titulo', 'tipo', 'prioridad', 'leido', 'fecha_envio', 'id_usuario')
    list_filter = ('tipo', 'prioridad', 'leido', 'fecha_envio')
    search_fields = ('titulo', 'mensaje', 'id_usuario__nombre')
    ordering = ('-fecha_envio',)
    readonly_fields = ('id_notificacion', 'fecha_envio')
    
    fieldsets = (
        ('Contenido', {
            'fields': ('titulo', 'mensaje', 'tipo', 'prioridad')
        }),
        ('Destinatario y Estado', {
            'fields': ('id_usuario', 'leido', 'fecha_envio')
        }),
    )
