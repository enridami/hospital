from django.urls import path
from .views import reception_dashboard_view

urlpatterns = [
    path('reception-dashboard/', reception_dashboard_view, name='reception_dashboard'),
]