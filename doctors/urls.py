from django.urls import path
from .views import doctor_dashboard_view

urlpatterns = [
    path('doctor-dashboard/', doctor_dashboard_view, name='doctor_dashboard'),
]