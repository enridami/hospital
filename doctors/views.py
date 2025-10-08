from django.shortcuts import render, redirect
from users.models import Doctor
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
@login_required
def doctor_dashboard_view(request):
    """Dashboard específico para doctores - PROTEGIDO"""
    # Primera protección: @login_required (usuario autenticado)

    # Segunda protección: verificar que sea doctor
    if not hasattr(request.user, 'doctor'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    
    doctor = request.user.doctor
    return render(request, 'doctors/doctor_dashboard.html',{
        'user': request.user,
        'doctor': doctor,
        'specialty': doctor.specialty.name,
    })