from django.db import models
from django.contrib.auth.models import AbstractUser

class Specialty(models.Model):
    """Modelo para especialidades médicas"""
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField()
   
    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"
       
    def __str__(self):
        return self.name



class Users(AbstractUser):
    """Modelo de usuario personalizado que extiende AbstractUser"""
    email = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=200)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
   
    # Opciones de género
    gender_choices = (("Male", "Male"), ("Female", "Female"))
    gender = models.CharField(max_length=10, choices=gender_choices, default="not_known")
    birthday = models.DateField(null=True, blank=True)
   
    # Campo específico para identificar doctores
    is_doctor = models.BooleanField(default=False)
   
    # Imagen de perfil
    profile_avatar = models.ImageField(
        upload_to="users/profiles",
        blank=True,
        default="users/profiles/default.png"
    )
   
    # Dirección
    address_line = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    code_postal = models.CharField(max_length=20, blank=True, null=True)


    # *** SOLUCIÓN AL CONFLICTO: Agregar related_name ***
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_users',  # Cambiar nombre del reverse accessor
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_users',  # Cambiar nombre del reverse accessor
        related_query_name='custom_user',
    )
   
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
       
    def __str__(self):
        return self.username




class Reset_token(models.Model):
    """Modelo para tokens de reset de contraseña"""
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    email = models.CharField(max_length=50, unique=True)
    token = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        verbose_name = "Reset Token"
        verbose_name_plural = "Reset Tokens"
       
    def __str__(self):
        return f"Reset token for {self.user.username}"
    


# Doctor
class Doctor(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    bio = models.TextField()

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctores"

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    

# Recepcion
class Receptions(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name = "Recepcion"
        verbose_name_plural = "Recepcionistas"

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
# Administrador
class Administrator(models.Model):
    """Modelo para administradores del sistema hospitalario"""
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=50, default="Administración") # Departamento del administrador
    can_create_users = models.BooleanField(default=True)
    can_create_groups = models.BooleanField(default=True)
    can_assign_roles = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
