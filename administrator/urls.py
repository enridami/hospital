from django.urls import path
from .views import admin_dashboard_view, admin_users_list, admin_create_user, admin_edit_user, admin_toggle_user_status, admin_create_staff, admin_create_doctor, admin_profile_view



urlpatterns = [
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    
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