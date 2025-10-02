from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, Specialty, Doctor, Administrator, Receptions, Reset_token, Patient

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

# Admin personalizado para Pacientes
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'identification_number', 'first_name', 'last_name', 
        'gender', 'age', 'phone', 'assigned_doctor', 'is_active'
    )
    list_filter = ('gender', 'blood_type', 'is_active', 'assigned_doctor', 'created_at')
    search_fields = (
        'first_name', 'last_name', 'identification_number', 
        'email', 'phone'
    )
    readonly_fields = ('age', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Identificación', {
            'fields': ('identification_type', 'identification_number')
        }),
        ('Información Demográfica', {
            'fields': ('gender', 'date_of_birth', 'age')
        }),
        ('Dirección', {
            'fields': ('address_line', 'city', 'region', 'postal_code', 'country')
        }),
        ('Información Médica', {
            'fields': ('blood_type', 'allergies', 'medical_notes', 'assigned_doctor')
        }),
        ('Contacto de Emergencia', {
            'fields': ('emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone')
        }),
        ('Sistema', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

# Register your models here.
admin.site.register(Users, CustomUserAdmin)
admin.site.register(Specialty)
admin.site.register(Doctor)
admin.site.register(Receptions)
admin.site.register(Administrator)
admin.site.register(Reset_token)
