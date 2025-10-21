from django.test import TestCase, Client
from django.urls import reverse
from users.models import Users, Doctor, DoctorSchedule, Specialty, Administrator
from django.contrib.auth.models import Permission

class DoctorScheduleTestCase(TestCase):
    def setUp(self):
        # Crear especialidad y usuario administrador
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
