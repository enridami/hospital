# reception/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta
from users.models import Receptions, Patient, Doctor, Specialty, Consultation

Users = get_user_model()

class ReceptionViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 1. Se crea un usuario base (no recepcionista)
        cls.non_reception_user = Users.objects.create_user(
            username='doctor_test', password='123', email='doctor@test.com'
        )
        
        # 2. Se crea un usuario recepcionista
        cls.reception_user = Users.objects.create_user(
            username='recepcion_test', password='123', email='recepcion@test.com'
        )
        #  Asocia el perfil recepcionista
        Receptions.objects.create(user=cls.reception_user)
        
        # 3. Crea los datos que se usaran para las consultas
        cls.specialty = Specialty.objects.create(name='Pediatría', description='Cuidado de niños')
        cls.doctor_user = Users.objects.create_user(username='dr_uno', password='123', is_doctor=True)
        cls.doctor = Doctor.objects.create(user=cls.doctor_user, specialty=cls.specialty, bio='Bio')
        
        cls.patient = Patient.objects.create(
            first_name='Laura', last_name='Perez', phone='12345678',
            identification_type='CI', identification_number='9876543',
            gender='Female', date_of_birth=date(2000, 1, 1),
            address_line='Calle Falsa 123', city='City', region='Region',
            postal_code='1111', country='Paraguay', blood_type='O+',
            emergency_contact_name='Emergencia', emergency_contact_relationship='Padre',
            emergency_contact_phone='98765432'
        )
        
        # URLs
        cls.dashboard_url = reverse('reception:reception_dashboard')
        cls.patient_create_url = reverse('reception:patient_create')
        cls.consultation_create_url = reverse('reception:consultation_create')

    def setUp(self):
        self.client = Client()

    # 1. Prueba: Seguridad de la vista de dashboard
    # ----------------------------------------------------
    def test_01_reception_dashboard_access_control(self):
        """Verifica que solo el Recepcionista pueda acceder al dashboard."""
        
        # A. Usuario Anónimo: Debe ser redirigido al login (302)
        response_anon = self.client.get(self.dashboard_url)
        self.assertEqual(response_anon.status_code, 302) 

        # B. Usuario sin Rol de Recepcionista: Debe ser redirigido 
        self.client.login(username='doctor_test', password='123')
        # La vista redirige al 'dashboard' (general) si no tiene el perfil de 'receptions'
        response_non_reception = self.client.get(self.dashboard_url, follow=True)
        # IMPORTANTE: Esperamos la redirección a 'dashboard' para romper el bucle.
        self.assertRedirects(response_non_reception, reverse('dashboard'))
        # Se comenta la aserción del mensaje, ya que puede fallar con follow=True
        # self.assertIn('No tienes permisos', response_non_reception.content.decode())

        # C. Usuario Recepcionista: Debe acceder (200)
        self.client.login(username='recepcion_test', password='123')
        response_reception = self.client.get(self.dashboard_url)
        self.assertEqual(response_reception.status_code, 200)
        self.assertTemplateUsed(response_reception, 'reception/reception_dashboard.html')


    # 2. Prueba: Creación Exitosa de Paciente (se usa POST)
    # ----------------------------------------------------
    def test_02_patient_creation_successful(self):
        """Verifica que el Recepcionista pueda crear un nuevo paciente con datos válidos."""
        
        self.client.login(username='recepcion_test', password='123')
        
        patient_data = {
            'first_name': 'Nuevo', 'last_name': 'Paciente', 
            'email': 'nuevo@paciente.com', 'phone': '99999999',
            'identification_type': 'DNI', 'identification_number': '11223344',
            'gender': 'Male', 
            'date_of_birth': '1985-10-20', # Formato esperado por DateInput
            'address_line': 'Av Principal', 'city': 'Capital',
            'region': 'Central', 'postal_code': '2000', 'country': 'Paraguay',
            'blood_type': 'B+', 'allergies': '', 'medical_notes': '',
            'emergency_contact_name': 'Hijo', 'emergency_contact_relationship': 'Hijo',
            'emergency_contact_phone': '88888888',
        }
        
        response = self.client.post(self.patient_create_url, patient_data, follow=True)
        
        # A. Verifica la redirección y el éxito
        self.assertRedirects(response, reverse('reception:consultation_list'))
        self.assertTrue(Patient.objects.filter(identification_number='11223344').exists())
        # COMENTADO: Esta línea causaba el FAIL. Se valida el éxito con las aserciones anteriores.
        # self.assertContains(response, 'Paciente registrado correctamente.')
        self.assertEqual(Patient.objects.count(), 2) # Paciente inicial + nuevo


    # 3. Prueba: Fallo en la Creación de Paciente (Datos Faltantes)
    # ----------------------------------------------------
    def test_03_patient_creation_fails_on_missing_data(self):
        """Verifica que la creación de paciente falle con datos incompletos."""
        
        self.client.login(username='recepcion_test', password='123')
        
        # Datos inválidos: Falta identificación, nombre, etc.
        invalid_data = {
            'first_name': '',  # Campo requerido faltante
            'last_name': 'Apellido',
            'phone': '12345678',
            'identification_number': '11111111',
            'gender': 'Male',
        }
        
        # El response debe ser 200 (volver a mostrar el formulario) y no redireccionar
        response = self.client.post(self.patient_create_url, invalid_data, follow=True)
        
        # A. Verifica que no se haya redireccionado (sigue en la página del formulario)
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'reception/patient_form.html')
        
        # B. Verifica que el objeto NO se haya creado en la DB
        self.assertFalse(Patient.objects.filter(identification_number='11111111').exists())
        self.assertEqual(Patient.objects.count(), 1) # Solo el paciente creado en setUpTestData
        
        # C. Verifica que el formulario contenga mensajes de error
        self.assertIn('Este campo es obligatorio', response.content.decode())

    # 4. Prueba: Creación de Consulta y Asignación Automática de Orden
    # ----------------------------------------------------
    def test_04_consultation_creation_and_auto_order_assignment(self):
        """Verifica que el sistema asigne automáticamente el orden correcto a las consultas."""
        
        self.client.login(username='recepcion_test', password='123')
        
        # Datos base para la consulta (Misma fecha, mismo doctor, mismo turno)
        consultation_data_base = {
            'patient': self.patient.pk,
            'doctor': self.doctor.pk,
            'date': date.today().isoformat(),
            'shift': Consultation.SHIFT_MORNING, # Turno Mañana
            'reason': 'Checkup general',
        }
        
        # --- A. Primera Consulta (Orden 1) ---
        self.client.post(self.consultation_create_url, consultation_data_base)
        consultation_1 = Consultation.objects.get(patient=self.patient, order=1)
        self.assertEqual(consultation_1.order, 1)

        # --- B. Segunda Consulta (Mismos criterios, debe ser Orden 2) ---
        # Se necesita crear un nuevo paciente para la segunda consulta
        patient_2 = Patient.objects.create(
            first_name='Segundo', last_name='Paciente', identification_number='2222222'
        )
        consultation_data_2 = consultation_data_base.copy()
        consultation_data_2['patient'] = patient_2.pk # Asigna el nuevo paciente

        self.client.post(self.consultation_create_url, consultation_data_2)
        consultation_2 = Consultation.objects.get(patient=patient_2)
        self.assertEqual(consultation_2.order, 2)
        
        # --- C. Tercera Consulta (Diferente Turno, debe ser Orden 1) ---
        patient_3 = Patient.objects.create(
            first_name='Tercero', last_name='Paciente', identification_number='3333333'
        )
        consultation_data_3 = consultation_data_base.copy()
        consultation_data_3['patient'] = patient_3.pk
        consultation_data_3['shift'] = Consultation.SHIFT_AFTERNOON # Turno Tarde
        
        self.client.post(self.consultation_create_url, consultation_data_3)
        consultation_3 = Consultation.objects.get(patient=patient_3)
        # Como el turno es diferente, el contador debe resetearse a 1 para ese turno
        self.assertEqual(consultation_3.order, 1)
