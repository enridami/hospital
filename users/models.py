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


# Paciente
class Patient(models.Model):
    """Modelo para pacientes del sistema hospitalario"""
    
    # Información personal básica
    first_name = models.CharField(max_length=50, verbose_name="Nombre")
    last_name = models.CharField(max_length=50, verbose_name="Apellido")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    
    # Identificación
    identification_type_choices = (
        ("CI", "CI"),
        ("DNI", "DNI"),
        ("Passport", "Pasaporte"),
        ("License", "Licencia de Conducir"),
        ("Other", "Otro")
    )
    identification_type = models.CharField(
        max_length=20, 
        choices=identification_type_choices, 
        default="CI",
        verbose_name="Tipo de Identificación"
    )
    identification_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Número de Identificación"
    )
    
    # Información demográfica
    gender_choices = (("Male", "Masculino"), ("Female", "Femenino"), ("Other", "Otro"))
    gender = models.CharField(
        max_length=10, 
        choices=gender_choices, 
        verbose_name="Género"
    )
    date_of_birth = models.DateField(verbose_name="Fecha de Nacimiento")
    
    # Dirección
    address_line = models.CharField(max_length=200, verbose_name="Dirección")
    city = models.CharField(max_length=50, verbose_name="Ciudad")
    region = models.CharField(max_length=50, verbose_name="Región/Estado")
    postal_code = models.CharField(max_length=20, verbose_name="Código Postal")
    country = models.CharField(max_length=50, default="Paraguay", verbose_name="País")
    
    # Información médica básica
    blood_type_choices = (
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
        ("Unknown", "Desconocido")
    )
    blood_type = models.CharField(
        max_length=10, 
        choices=blood_type_choices, 
        default="Unknown",
        verbose_name="Tipo de Sangre"
    )
    allergies = models.TextField(blank=True, null=True, verbose_name="Alergias")
    medical_notes = models.TextField(blank=True, null=True, verbose_name="Notas Médicas")
    
    # Contacto de emergencia
    emergency_contact_name = models.CharField(
        max_length=100, 
        verbose_name="Nombre del Contacto de Emergencia"
    )
    emergency_contact_relationship = models.CharField(
        max_length=50, 
        verbose_name="Relación del Contacto"
    )
    emergency_contact_phone = models.CharField(
        max_length=20, 
        verbose_name="Teléfono del Contacto de Emergencia"
    )
    
    # Información del sistema
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    # Doctor asignado (opcional)
    assigned_doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Doctor Asignado"
    )

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.identification_number}"
    
    @property
    def full_name(self):
        """Retorna el nombre completo del paciente"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calcula la edad del paciente"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    



# Creación de modelos de tabla Consultas y Recetas

class Consultation(models.Model):
    """Modelo para consultas médicas"""
    description = models.TextField(verbose_name="Descripción")
    date = models.DateField(verbose_name="Fecha")
    time = models.TimeField(verbose_name="Hora")

    # Campo de turno
    shift_choices = (
        ("MAÑANA", "Mañana"),
        ("TARDE", "Tarde"),
        ("NOCHE", "Noche"),
    )
    shift = models.CharField(
        max_length=10,
        choices=shift_choices,
        default="MAÑANA",
        verbose_name="Turno"
    )

    # Campo de orden en la cola de atención
    order = models.PositiveIntegerField(verbose_name="Orden", default=1)
    
    # Opciones de prioridad
    priority_choices = (
        ("NIVEL I", "Nivel I"),
        ("Nivel II", "Nivel II"),
        ("Nivel III", "Nivel III"),
        ("Nivel IV", "Nivel IV"),
        ("Nivel V", "Nivel V"),
    )
    priority = models.CharField(
        max_length=10,
        choices=priority_choices,
        default="Nivel IV",
        verbose_name="Prioridad"
    )
    
    consultorio = models.CharField(max_length=10, blank=False, null=False, default="")
    servicio = models.ForeignKey('Specialty', on_delete=models.SET_NULL, null=True, blank=True)
    temperatura = models.FloatField(blank=False, null=False, default=0)
    presion_sistolica = models.IntegerField(blank=False, null=False, default=0)
    presion_diastolica = models.IntegerField(blank=False, null=False, default=0)
    frecuencia_respiratoria = models.IntegerField(blank=False, null=False, default=0)
    pulso = models.IntegerField(blank=False, null=False, default=0)
    saturacion_oxigeno = models.IntegerField(blank=False, null=False, default=0)
    peso = models.FloatField(blank=False, null=False, default=0)
    talla = models.FloatField(blank=False, null=False, default=0)
    circunferencia_abdominal = models.FloatField(blank=False, null=False, default=0)
    historia_actual = models.TextField(blank=False, null=False, default="")
    evolucion = models.TextField(blank=False, null=False, default="")
    impresion_diagnostica = models.TextField(blank=False, null=False, default="")
    hba1c = models.FloatField(blank=False, null=False, default=0)
    indicaciones = models.TextField(blank=False, null=False, default="")


    # Opciones de estado
    status_choices = (
        ("EN ESPERA", "En espera"),
        ("ATENDIDO", "Atendido"),
        ("CANCELADA", "Cancelada"),
    )
    status = models.CharField(
        max_length=15,
        choices=status_choices,
        default="EN ESPERA",
        verbose_name="Estado"
    )
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Médico"
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        verbose_name="Paciente"
    )

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ['-date', '-time']

    def __str__(self):
        return f"Consulta de {self.patient.full_name} con {self.doctor} el {self.date} a las {self.time}"



# TABLA RECETAS
class Prescription(models.Model):
    """Modelo para recetas médicas"""
    medication = models.CharField(max_length=100, verbose_name="Medicamento")
    description = models.TextField(verbose_name="Descripción")
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Médico"
    )
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        verbose_name="Consulta"
    )

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        ordering = ['-id']

    def __str__(self):
        return f"Receta para {self.consultation.patient.full_name} - {self.medication}"
    
