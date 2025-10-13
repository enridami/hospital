from django.urls import path
from .views import reception_dashboard_view
from . import views

urlpatterns = [
    path('reception-dashboard/', reception_dashboard_view, name='reception_dashboard'),
    path('consultas/', views.consultation_list_view, name='consultation_list'),
    path('consultas/nueva/', views.consultation_create_view, name='consultation_create'),
    path('consultas/<int:pk>/editar/', views.consultation_edit_view, name='consultation_edit'),
    path('consultas/<int:pk>/eliminar/', views.consultation_delete_view, name='consultation_delete'),
    path('pacientes/nuevo/', views.patient_create_view, name='patient_create'),
    path('perfil/', views.reception_profile_view, name='profile'),
    path('pacientes/', views.patient_list_view, name='patient_list'),
    path('pacientes/', views.patient_list_view, name='patient_list'),
    path('pacientes/<int:pk>/editar/', views.patient_edit_view, name='patient_edit'),
    path('pacientes/<int:pk>/eliminar/', views.patient_delete_view, name='patient_delete'),

    # Consultas realizadas
    path('consultations/history/', views.consultation_history_view, name='consultation_history')
    
    
]