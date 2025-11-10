from django.test import TestCase
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse, NoReverseMatch
from users.models import Users, Specialty, Doctor, Receptions, DoctorSchedule, Patient, Consultation


#*** PRUEBA 1 ***
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


#*** PRUEBA 2 ***
# python manage.py test mytests.tests.test_integration.ReceptionDoctorFlowIT -v 2

def safe_reverse(testcase, name, *args, **kwargs):
    try:
        return reverse(name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        testcase.skipTest(f"Falta la URL '{name}'. Ajusta el nombre en urls.py.")

class ReceptionDoctorFlowIT(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.specialty = Specialty.objects.create(name="Cardiología", description="Corazón")
        cls.reception_user = Users.objects.create_user(
            username='reception', password='pass12345', email='r@example.com',
            first_name='Rec', last_name='Eption'
        )
        Receptions.objects.create(user=cls.reception_user)
        cls.doctor_user = Users.objects.create_user(
            username='doctor', password='pass12345', email='d@example.com',
            first_name='Doc', last_name='Tor', is_doctor=True
        )
        cls.doctor = Doctor.objects.create(user=cls.doctor_user, specialty=cls.specialty, bio="Bio")
        # Horario que cubra la hora que usaremos (09:00 dentro de 08:00-12:00)
        DoctorSchedule.objects.create(
            doctor=cls.doctor,
            day='LUNES',
            start_time=timezone.datetime(2025,1,6,8,0).time(),
            end_time=timezone.datetime(2025,1,6,12,0).time(),
            consultorio='A101'
        )
        # Paciente (todos los campos requeridos)
        cls.patient = Patient.objects.create(
            first_name='Juan', last_name='Pérez',
            email='jp@example.com', phone='+5951234567',
            identification_type='CI', identification_number='12345678',
            gender='Male', date_of_birth=timezone.datetime(1990,1,1).date(),
            address_line='Calle 1', city='Asunción', region='Central',
            postal_code='1234', country='Paraguay',
            blood_type='O+', emergency_contact_name='Maria',
            emergency_contact_relationship='Madre',
            emergency_contact_phone='+595987654321'
        )

    def test_reception_creates_consultation(self):
        self.assertTrue(self.client.login(username='reception', password='pass12345'))
        # Fecha un lunes (coincide con horario)
        target_date = timezone.datetime(2025,1,6).date()
        # GET para preparar paciente y doctores
        create_url = safe_reverse(self, 'reception:consultation_create')
        get_resp = self.client.get(
            create_url,
            {'ci_query': self.patient.identification_number, 'especialidad': self.specialty.id},
            follow=True
        )
        self.assertEqual(get_resp.status_code, 200)

        post_payload = {
            'doctor': self.doctor.id,
            'description': 'Dolor torácico',
            'date': target_date.strftime('%Y-%m-%d'),
            'time': '09:00',
            'shift': 'MAÑANA',
            'priority': 'Nivel IV',
            'turno_auto': 'MAÑANA',
        }
        post_resp = self.client.post(create_url, data=post_payload, follow=True)
        self.assertIn(post_resp.status_code, (200, 302))

        consulta = Consultation.objects.filter(patient=self.patient, doctor=self.doctor, date=target_date).first()
        self.assertIsNotNone(consulta, "Consulta no creada")
        self.assertEqual(consulta.consultorio, 'a101', "Consultorio no asignado según horario (debería normalizarse a minúsculas)")
        self.assertEqual(consulta.order, 1, "Order inicial incorrecto")
        self.assertEqual(consulta.status, 'EN ESPERA')

    def test_doctor_marks_consultation_attended(self):
        # Crear consulta directamente (pre-condición)
        consulta = Consultation.objects.create(
            description='Control',
            date=timezone.datetime(2025,1,6).date(),
            time=timezone.datetime(2025,1,6,9,0).time(),
            shift='MAÑANA',
            order=1,
            priority='Nivel IV',
            consultorio='a101',
            doctor=self.doctor,
            patient=self.patient,
            status='EN ESPERA'
        )
        self.assertTrue(self.client.login(username='doctor', password='pass12345'))
        status_url = safe_reverse(self, 'change_consultation_status', consulta.id)
        resp = self.client.post(status_url, {'nuevo_estado': 'ATENDIDO'}, follow=True)
        self.assertIn(resp.status_code, (200, 302))
        consulta.refresh_from_db()
        self.assertEqual(consulta.status, 'ATENDIDO', "Estado no actualizado a ATENDIDO")
