"""
Modelos de la aplicación de usuarios.

Este módulo contiene los modelos para la gestión de usuarios, pacientes, doctores, administradores, recepcionistas, especialidades, consultas y recetas médicas.

- Usuarios personalizados
- Especialidades médicas
- Doctores, recepcionistas y administradores
- Pacientes y sus datos médicos
- Consultas y recetas

.. moduleauthor:: enridami
"""
from django.db import models
from django.contrib.auth.models import AbstractUser

class Specialty(models.Model):
    """
    Modelo para especialidades médicas.

    :param name: Nombre de la especialidad
    :type name: str
    :param description: Descripción de la especialidad
    :type description: str
    :return: Nombre de la especialidad
    :rtype: str
    """
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField()
   
    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"
       
    def __str__(self):
        return self.name



class Users(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.

    :param email: Email único del usuario
    :type email: str
    :param username: Nombre de usuario único
    :type username: str
    :param password: Contraseña encriptada
    :type password: str
    :param first_name: Nombre
    :type first_name: str
    :param last_name: Apellido
    :type last_name: str
    :param gender: Género del usuario
    :type gender: str
    :param birthday: Fecha de nacimiento
    :type birthday: date
    :param is_doctor: Indica si el usuario es doctor
    :type is_doctor: bool
    :param profile_avatar: Imagen de perfil
    :type profile_avatar: ImageField
    :param address_line: Dirección
    :type address_line: str
    :param region: Región
    :type region: str
    :param city: Ciudad
    :type city: str
    :param code_postal: Código postal
    :type code_postal: str
    :return: Nombre de usuario
    :rtype: str
    """
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
    """
    Modelo para tokens de reset de contraseña.

    :param user: Usuario relacionado
    :type user: Users
    :param email: Email único
    :type email: str
    :param token: Token de recuperación
    :type token: str
    :param created_at: Fecha de creación
    :type created_at: datetime
    :return: Token para el usuario
    :rtype: str
    """
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
    """
    Modelo para doctores del sistema hospitalario.

    :param user: Usuario relacionado
    :type user: Users
    :param specialty: Especialidad médica
    :type specialty: Specialty
    :param bio: Biografía del doctor
    :type bio: str
    :param consultorio: Consultorio asignado
    :type consultorio: str
    :return: Nombre completo del doctor
    :rtype: str
    """
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    bio = models.TextField()
    consultorio = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctores"

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    

# Recepcion
class Receptions(models.Model):
    """
    Modelo para recepcionistas del sistema hospitalario.

    :param user: Usuario relacionado
    :type user: Users
    :return: Nombre completo del recepcionista
    :rtype: str
    """
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name = "Recepcion"
        verbose_name_plural = "Recepcionistas"

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
# Administrador
class Administrator(models.Model):
    """
    Modelo para administradores del sistema hospitalario.

    :param user: Usuario relacionado
    :type user: Users
    :param department: Departamento del administrador
    :type department: str
    :param can_create_users: Permiso para crear usuarios
    :type can_create_users: bool
    :param can_create_groups: Permiso para crear grupos
    :type can_create_groups: bool
    :param can_assign_roles: Permiso para asignar roles
    :type can_assign_roles: bool
    :return: Nombre completo del administrador
    :rtype: str
    """
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
    """
    Modelo para pacientes del sistema hospitalario.

    :param first_name: Nombre
    :type first_name: str
    :param last_name: Apellido
    :type last_name: str
    :param email: Email
    :type email: str
    :param phone: Teléfono
    :type phone: str
    :param identification_type: Tipo de identificación
    :type identification_type: str
    :param identification_number: Número de identificación
    :type identification_number: str
    :param gender: Género
    :type gender: str
    :param date_of_birth: Fecha de nacimiento
    :type date_of_birth: date
    :param address_line: Dirección
    :type address_line: str
    :param city: Ciudad
    :type city: str
    :param region: Región/Estado
    :type region: str
    :param postal_code: Código postal
    :type postal_code: str
    :param country: País
    :type country: str
    :param blood_type: Tipo de sangre
    :type blood_type: str
    :param allergies: Alergias
    :type allergies: str
    :param medical_notes: Notas médicas
    :type medical_notes: str
    :param emergency_contact_name: Nombre del contacto de emergencia
    :type emergency_contact_name: str
    :param emergency_contact_relationship: Relación del contacto
    :type emergency_contact_relationship: str
    :param emergency_contact_phone: Teléfono del contacto de emergencia
    :type emergency_contact_phone: str
    :param created_at: Fecha de registro
    :type created_at: datetime
    :param updated_at: Última actualización
    :type updated_at: datetime
    :param is_active: Estado activo
    :type is_active: bool
    :param assigned_doctor: Doctor asignado
    :type assigned_doctor: Doctor
    :return: Nombre completo del paciente
    :rtype: str
    """
    
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
    """
    Modelo para consultas médicas.

    :param description: Descripción de la consulta
    :type description: str
    :param date: Fecha
    :type date: date
    :param time: Hora
    :type time: time
    :param shift: Turno
    :type shift: str
    :param order: Orden en la cola
    :type order: int
    :param priority: Prioridad
    :type priority: str
    :param consultorio: Consultorio
    :type consultorio: str
    :param servicio: Servicio/especialidad
    :type servicio: Specialty
    :param temperatura: Temperatura
    :type temperatura: float
    :param presion_sistolica: Presión sistólica
    :type presion_sistolica: int
    :param presion_diastolica: Presión diastólica
    :type presion_diastolica: int
    :param frecuencia_respiratoria: Frecuencia respiratoria
    :type frecuencia_respiratoria: int
    :param pulso: Pulso
    :type pulso: int
    :param saturacion_oxigeno: Saturación de oxígeno
    :type saturacion_oxigeno: int
    :param peso: Peso
    :type peso: float
    :param talla: Talla
    :type talla: float
    :param circunferencia_abdominal: Circunferencia abdominal
    :type circunferencia_abdominal: float
    :param historia_actual: Historia actual
    :type historia_actual: str
    :param evolucion: Evolución
    :type evolucion: str
    :param impresion_diagnostica: Impresión diagnóstica
    :type impresion_diagnostica: str
    :param hba1c: HbA1c
    :type hba1c: float
    :param indicaciones: Indicaciones
    :type indicaciones: str
    :param status: Estado
    :type status: str
    :param doctor: Médico
    :type doctor: Doctor
    :param patient: Paciente
    :type patient: Patient
    :return: Descripción de la consulta
    :rtype: str
    """
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
    temperatura = models.FloatField(blank=True, null=True)
    presion_sistolica = models.IntegerField(blank=True, null=True)
    presion_diastolica = models.IntegerField(blank=True, null=True)
    frecuencia_respiratoria = models.IntegerField(blank=True, null=True)
    pulso = models.IntegerField(blank=True, null=True)
    saturacion_oxigeno = models.IntegerField(blank=True, null=True)
    peso = models.FloatField(blank=True, null=True)
    talla = models.FloatField(blank=True, null=True)
    circunferencia_abdominal = models.FloatField(blank=True, null=True)
    historia_actual = models.TextField(blank=True, null=True, default="")
    evolucion = models.TextField(blank=True, null=True, default="")
    impresion_diagnostica = models.TextField(blank=True, null=True, default="")
    hba1c = models.FloatField(blank=True, null=True)
    indicaciones = models.TextField(blank=True, null=True, default="")


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
    """
    Modelo para recetas médicas.

    :param medication: Medicamento
    :type medication: str
    :param description: Descripción
    :type description: str
    :param doctor: Médico
    :type doctor: Doctor
    :param consultation: Consulta relacionada
    :type consultation: Consultation
    :return: Descripción de la receta
    :rtype: str
    """
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
    
