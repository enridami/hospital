"""
Configuración de la aplicación de usuarios.

Este módulo contiene la configuración principal de la aplicación users.
- Define el campo de auto incremento por defecto
- Define el nombre de la aplicación

.. moduleauthor:: enridami
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Clase de configuración para la aplicación users.

    :param default_auto_field: Campo de auto incremento por defecto
    :type default_auto_field: str
    :param name: Nombre de la aplicación
    :type name: str
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
