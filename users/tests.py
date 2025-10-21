"""
Pruebas unitarias para la aplicación de usuarios.

Este módulo contiene las pruebas para verificar el correcto funcionamiento de:
- Creación de usuarios
- Autenticación
- Funcionalidades específicas de la aplicación

.. moduleauthor:: enridami
"""

from django.test import TestCase
from django.contrib.auth.models import User

class UserModelTest(TestCase):
    """
    Pruebas para el modelo de Usuario.
    
    Verifica la correcta creación y autenticación de usuarios.
    """
    
    def test_create_user(self):
        """
        Prueba la creación de un usuario y verifica sus credenciales.
        
        :return: None
        """
        user = User.objects.create_user(username='testuser', password='12345')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('12345'))