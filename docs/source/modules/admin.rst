Admin
=====

Configuración del panel de administración Django para la aplicación de usuarios.

Este módulo define la personalización del panel admin, incluyendo:
- CustomUserAdmin: Configuración personalizada para el modelo Users
- PatientAdmin: Configuración personalizada para el modelo Patient
- Registro de otros modelos en el panel de administración

Clases
------

.. autoclass:: users.admin.CustomUserAdmin
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: users.admin.PatientAdmin
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Registro de Modelos
------------------

Los siguientes modelos están registrados en el panel de administración:

* Users (con CustomUserAdmin)
* Specialty
* Doctor
* Receptions
* Administrator
* Reset_token
* Patient (con PatientAdmin)