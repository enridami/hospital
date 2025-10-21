URLs
====

Configuración de URLs para la aplicación de usuarios.

Este módulo define las rutas URL disponibles para la aplicación, incluyendo:

* Rutas de autenticación (login/logout)
* Dashboards
* Inclusión de otras apps (doctors, reception, administrator)
* Configuración de archivos estáticos

Patrones de URL
--------------

* ``/`` - Vista de inicio de sesión
* ``/login/`` - Vista de inicio de sesión
* ``/logout/`` - Vista de cierre de sesión
* ``/dashboard/`` - Dashboard general
* ``/password-reset/`` - Recuperación de contraseña
* ``/doctors/`` - Inclusión de URLs de doctores
* ``/reception/`` - Inclusión de URLs de recepción
* ``/administrator/`` - Inclusión de URLs de administrador

Configuración de Archivos Estáticos
---------------------------------

El módulo configura automáticamente las URLs para servir:

* Archivos estáticos (STATIC_URL)
* Archivos multimedia (MEDIA_URL)
* Patrones de archivos estáticos adicionales