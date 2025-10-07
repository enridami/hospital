from django.urls import path
from .views import login_view, logout_view, dashboard_view, doctor_dashboard_view, reception_dashboard_view, admin_dashboard_view, admin_users_list, admin_create_user, admin_edit_user, admin_toggle_user_status, admin_create_staff, admin_create_doctor, admin_profile_view
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'), # Dashboard general
    path('doctor-dashboard/', doctor_dashboard_view, name='doctor_dashboard'),
    path('reception-dashboard/', reception_dashboard_view, name='reception_dashboard'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('password-reset/', login_view, name='password-reset'), #temporal para que pueda recuperar contraseña
    
    # URLs para gestión de usuarios
    path('admin-dashboard/users/', admin_users_list, name='admin_users_list'),
    path('admin-dashboard/users/create/', admin_create_user, name='admin_create_user'),
    path('admin-dashboard/users/edit/<int:user_id>/', admin_edit_user, name='admin_edit_user'),
    path('admin-dashboard/users/toggle-status/<int:user_id>/', admin_toggle_user_status, name='admin_toggle_user_status'),
    
    # URLs para gestión de doctores y personal
    path('admin-dashboard/doctors/create/', admin_create_doctor, name='admin_create_doctor'),
    path('admin-dashboard/staff/create/', admin_create_staff, name='admin_create_staff'),

    # URLs para gestión de administrador
    path('admin-dashboard/profile/', admin_profile_view, name='admin_profile'),
    
    
]

# Configuración para servir archivos estáticos en desarrollo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()

