from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, Specialty, Doctor, Administrator, Receptions, Reset_token

# Información adicional al registrar usuario

class CustomUserAdmin(UserAdmin):
    # Campos a mostrar en la lista
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    
    # Campos a mostrar al editar usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('gender', 'birthday', 'is_doctor', 'profile_avatar', 'address_line', 'region', 'city', 'code_postal')
        }),
    )
    
    # Campos a mostrar al crear usuario (SIN last_login)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Información Adicional', {
            'fields': ('gender', 'birthday', 'is_doctor', 'profile_avatar', 'address_line', 'region', 'city', 'code_postal')
        }),
    )

# Register your models here.
admin.site.register(Users, CustomUserAdmin)
admin.site.register(Specialty)
admin.site.register(Doctor)
admin.site.register(Receptions)
admin.site.register(Administrator)
admin.site.register(Reset_token)
