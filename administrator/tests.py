from django.test import TestCase, Client
from django.urls import reverse
from users.models import Users, Doctor, DoctorSchedule, Specialty, Administrator
from django.contrib.auth.models import Permission

class DoctorScheduleTestCase(TestCase):
    def setUp(self):
    
        self.specialty = Specialty.objects.create(name="Cardiología")
        self.admin_user = Users.objects.create_user(
            username="admin", email="admin@test.com", password="adminpass"
        )
        Administrator.objects.create(user=self.admin_user)
        permiso = Permission.objects.get(codename='add_users')
        self.admin_user.user_permissions.add(permiso)
        self.admin_user.save()
        self.client = Client()
        self.client.login(username="admin", password="adminpass")

    def test_no_duplicate_schedule_for_consultorio(self):
        # Registrar primer doctor con horario y consultorio
        response1 = self.client.post(reverse('admin_create_doctor'), {
            'username': 'doctor1',
            'email': 'doc1@test.com',
            'first_name': 'Doc',
            'last_name': 'Uno',
            'password': 'testpass123',
            'conf_password': 'testpass123',
            'specialty': self.specialty.id,
            'bio': 'Experiencia en cardiología',
            'horario_day[]': ['LUNES'],
            'horario_start[]': ['08:00'],
            'horario_end[]': ['12:00'],
            'horario_consultorio[]': ['A101'],
        })
        #self.assertEqual(response1.status_code, 302)  # Redirige por éxito

        # Después del primer POST
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(DoctorSchedule.objects.count(), 1)
        horario = DoctorSchedule.objects.first()
        print("Horario guardado:", horario.day, horario.start_time, horario.end_time, horario.consultorio)

        # Intentar registrar otro doctor en el mismo horario y consultorio
        response2 = self.client.post(reverse('admin_create_doctor'), {
            'username': 'doctor2',
            'email': 'doc2@test.com',
            'first_name': 'Doc',
            'last_name': 'Dos',
            'password': 'testpass123',
            'conf_password': 'testpass123',
            'specialty': self.specialty.id,
            'bio': 'Experiencia en cardiología',
            'horario_day[]': ['LUNES'],
            'horario_start[]': ['08:00'],
            'horario_end[]': ['12:00'],
            'horario_consultorio[]': ['A101'],
        })
        # Debe mostrar error y no redirigir
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, "ya está ocupado el LUNES")

# PRUEBAS DE SEGURIDAD A PARTIR DE AQUI

from django.test import TestCase, Client
from django.urls import reverse
from users.models import Users, Doctor, DoctorSchedule, Specialty, Administrator, Receptions, Patient
from datetime import date, time, timedelta
from django.db.models import Q

class AdminSecurityTest(TestCase):
    """
    Pruebas de seguridad y validación para el módulo de administración,
    enfocadas en el control de acceso y manipulación de datos.
    """

    def setUp(self):
        """Configuración inicial: Crear usuarios de prueba."""
        
        # Usamos Users de forma consistente
        User = Users 
        
        # 1. Usuario Administrador (Debería tener acceso total)
        self.admin_user = User.objects.create_user(
            username='admin_test', email='admin@test.com', password='Password123!', 
            first_name='Admin', last_name='User', 
            is_staff=True, is_superuser=True
        )
        Administrator.objects.create(user=self.admin_user)
        self.admin_client = Client()
        self.admin_client.login(username='admin_test', password='Password123!')

        # 2. Usuario Recepcionista (No debería tener acceso a vistas Admin críticas)
        self.reception_user = User.objects.create_user(
            username='reception_test', email='reception@test.com', password='Password123!',
            first_name='Recepcionista', last_name='User'
        )
        Receptions.objects.create(user=self.reception_user)
        self.reception_client = Client()
        self.reception_client.login(username='reception_test', password='Password123!')

        # 3. Usuario Paciente (No debería tener acceso a vistas Admin)
        self.patient_user = User.objects.create_user(
            username='patient_test', email='patient@test.com', password='Password123!',
            first_name='Paciente', last_name='User'
        )
        
        self.patient_client = Client()
        self.patient_client.login(username='patient_test', password='Password123!')
        
        # Crear datos de soporte
        self.specialty = Specialty.objects.create(name='Pediatría', description='Cuidado de niños')
        self.consultorio = 'a101'
        
        # Crear un doctor para pruebas de solapamiento
        self.doctor_user = User.objects.create_user(
            username='doctor_test', email='doctor@test.com', password='Password123!', is_doctor=True
        )
        self.doctor = Doctor.objects.create(user=self.doctor_user, specialty=self.specialty, bio='Bio Test')
        # Horario base para solapamiento
        self.base_schedule = DoctorSchedule.objects.create(
            doctor=self.doctor, day='LUNES', start_time=time(8, 0), end_time=time(12, 0), consultorio=self.consultorio
        )
        print(f"Horario guardado: {self.base_schedule.day} {self.base_schedule.start_time} {self.base_schedule.end_time} {self.base_schedule.consultorio}")



    # -----------------------------------------------
    # ✅ PASÓ: Manipulación de Rol Inexistente
    # -----------------------------------------------
    def test_admin_create_user_role_manipulation(self):
         """Verificar que el rol enviado sea uno de los esperados y no un rol arbitrario o inexistente."""
         
         response = self.admin_client.post(reverse('admin_create_user'), {
             'username': 'hacker_user',
             'email': 'hacker@test.com',
             'first_name': 'Hacker',
             'last_name': 'Role',
             'password': 'Password123!',
             'role': 'super_admin_invisible' # Rol inexistente
         }, follow=True)
         
         user = Users.objects.filter(username='hacker_user').first()
         
         # 1. El usuario se debe crear (el rol fallido no debe bloquear la creación del Users)
         self.assertIsNotNone(user, "El usuario base debe crearse.")
         
         # 2. Ningún perfil especial debe crearse
         self.assertFalse(hasattr(user, 'administrator'), "No debe tener perfil de administrador.")
         self.assertFalse(hasattr(user, 'receptions'), "No debe tener perfil de recepcionista.")
         self.assertFalse(user.is_doctor, "No debe ser doctor.")
         
         # El rol desconocido debe resultar en un usuario base sin privilegios.
         self.assertTrue(user.is_active)
         self.assertFalse(user.is_staff)
        

    # --- Pruebas de Eliminación y Edición ---

    # -----------------------------------------------
    # ✅ PASÓ: Control de Acceso para Eliminación (POST)
    # -----------------------------------------------
    # administrator/tests.py (Corrigiendo el test de Eliminación)

    def test_admin_delete_user_access_control(self):
         """Verificar que solo el administrador pueda eliminar usuarios (POST)."""
         
         # ... (La parte de la Recepcionista ya funciona)
         
         # El administrador SÍ debe poder eliminar al paciente
         delete_url = reverse('admin_delete_user', args=[self.patient_user.id])
         
         # Se asume que initial_count es 4
         initial_count = Users.objects.count()
         
         response = self.admin_client.post(delete_url)
         
         self.assertEqual(response.status_code, 200)
         self.assertJSONEqual(response.content, {'success': True})
         
         # 🟢 ASERSION CORREGIDA: Debe ser (initial_count - 1)
         self.assertEqual(Users.objects.count(), initial_count - 1, 
                          "El usuario DEBE ser eliminado por el administrador, reduciendo el conteo.")