from django.test import TestCase
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse, NoReverseMatch
from users.models import Users, Specialty, Doctor, Receptions, DoctorSchedule, Patient, Consultation
from datetime import date, time


# python manage.py test mytests.tests.test_integration.DBIntegrationTest -v 2

class DBIntegrationTest(TestCase):
    def test_db_select_1(self):
        with connection.cursor() as cur:
            cur.execute("SELECT 1;")
            self.assertEqual(cur.fetchone()[0], 1)

    def test_create_and_authenticate_user(self):
        User = get_user_model()
        User.objects.create_user(username='it_user', password='pass12345')
        self.assertTrue(self.client.login(username='it_user', password='pass12345'))




# python manage.py test mytests.tests.test_integration.BasicFlow -v 2
class BasicFlow(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Especialidad
        cls.specialty = Specialty.objects.create(name="Cardiología", description="Corazón")
        # Usuario recepcionista
        cls.reception_user = Users.objects.create_user(
            username='reception', email='r@example.com', password='pass12345',
            first_name='Rec', last_name='Eption'
        )
        Receptions.objects.create(user=cls.reception_user)
        # Usuario doctor
        cls.doctor_user = Users.objects.create_user(
            username='doctor', email='d@example.com', password='pass12345',
            first_name='Doc', last_name='Tor', is_doctor=True
        )
        cls.doctor = Doctor.objects.create(user=cls.doctor_user, specialty=cls.specialty, bio="Bio")
        # Horario del doctor
        DoctorSchedule.objects.create(
            doctor=cls.doctor,
            day='LUNES',
            start_time=time(8, 0),
            end_time=time(12, 0),
            consultorio='a101'
        )
    
    def test_1_create_patient_via_view(self):
        self.assertTrue(self.client.login(username='reception', password='pass12345'))
        url = reverse('patient_create')
        payload = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'jp@example.com',
            'phone': '+5951234567',
            'identification_type': 'CI',
            'identification_number': '99900011',
            'gender': 'Male',
            'date_of_birth': '1990-01-01',
            'address_line': 'Calle 1',
            'city': 'Asunción',
            'region': 'Central',
            'postal_code': '1234',
            'country': 'Paraguay',
            'blood_type': 'O+',
            'allergies': '',
            'medical_notes': '',
            'emergency_contact_name': 'Maria',
            'emergency_contact_relationship': 'Madre',
            'emergency_contact_phone': '+595987654321'
        }
        resp = self.client.post(url, data=payload, follow=True)
        self.assertIn(resp.status_code, (200, 302))
        self.assertTrue(Patient.objects.filter(identification_number='99900011').exists(), "Paciente no creado")

    def _create_patient_for_consultation(self):
        return Patient.objects.create(
            first_name='Ana', last_name='Gómez',
            email='ag@example.com', phone='+595111222333',
            identification_type='CI', identification_number='12345678',
            gender='Female', date_of_birth=date(1995, 5, 5),
            address_line='Av 2', city='Asunción', region='Central',
            postal_code='2000', country='Paraguay',
            blood_type='O+', emergency_contact_name='Luis',
            emergency_contact_relationship='Padre',
            emergency_contact_phone='+595444555666'
        )
    
    def test_2_attend_consultation(self):
        patient = self._create_patient_for_consultation()
        consulta = Consultation.objects.create(
            description='Dolor torácico',
            date=date(2025, 1, 6),
            time=time(9, 0),
            shift='MAÑANA',
            order=1,
            priority='Nivel IV',
            consultorio='a101',
            status='EN ESPERA',
            doctor=self.doctor,
            patient=patient
        )
        self.assertTrue(self.client.login(username='doctor', password='pass12345'))
        url = reverse('attend_consultation', args=[consulta.pk])
        attend_payload = {
            'description': consulta.description,
            'temperatura': 36.7,
            'frecuencia_respiratoria': 18,
            'pulso': 72,
            'presion_sistolica': 120,
            'presion_diastolica': 80,
            'saturacion_oxigeno': 97,
            'peso': 70,
            'talla': 1.75,
            'circunferencia_abdominal': 85,
            'historia_actual': 'Inicio hace 2 días.',
            'evolucion': 'Mejorando.',
            'impresion_diagnostica': 'Probable cuadro viral.',
            'hba1c': '',
            'indicaciones': 'Reposo e hidratación.'
        }
        resp = self.client.post(url, data=attend_payload, follow=True)
        self.assertIn(resp.status_code, (200, 302))
        consulta.refresh_from_db()
        self.assertEqual(consulta.status, 'ATENDIDO')
        self.assertEqual(consulta.servicio, self.specialty)

    def test_3_change_consultation_status(self):
        patient = self._create_patient_for_consultation()
        consulta = Consultation.objects.create(
            description='Control',
            date=date.today(),
            time=time(10, 0),
            shift='MAÑANA',
            order=1,
            priority='Nivel IV',
            consultorio='a101',
            status='EN ESPERA',
            doctor=self.doctor,
            patient=patient
        )
        self.assertTrue(self.client.login(username='doctor', password='pass12345'))
        url = reverse('change_consultation_status', args=[consulta.pk])
        resp = self.client.post(url, {'nuevo_estado': 'CANCELADA'}, follow=True)
        self.assertIn(resp.status_code, (200, 302))
        consulta.refresh_from_db()
        self.assertEqual(consulta.status, 'CANCELADA')