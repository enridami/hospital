from django.urls import path
from .views import doctor_dashboard_view
from . import views

urlpatterns = [
    path('doctor-dashboard/', doctor_dashboard_view, name='doctor_dashboard'),
    path('profile/', views.doctor_profile_view, name='doctor_profile'),
    path('patients/', views.doctor_patient_list_view, name='doctor_patient_list'),
    path('consultation/<int:consultation_id>/change-status/', views.change_consultation_status_view, name='change_consultation_status'),
    path('consultation-history/', views.doctor_consultation_history_view, name='doctor_consultation_history'),
    path('consultation/<int:consultation_id>/attend/', views.attend_consultation_view, name='attend_consultation'),
    path('consultation/edit/<int:id>/', views.edit_consultation, name='edit_consultation')
    
]