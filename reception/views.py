from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Consultation, Patient, Doctor
from .forms import PatientForm, ConsultationForm

# Dashboard principal
@login_required
def reception_dashboard_view(request):
    """Dashboard específico para recepcionistas - PROTEGIDO"""
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    return render(request, 'reception/reception_dashboard.html', {
        'user': request.user,
    })

# Listar consultas
@login_required
def consultation_list_view(request):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    consultas = Consultation.objects.all().order_by('date', 'shift', 'order')
    return render(request, 'reception/manage_medical_shifts.html', {
        'consultations': consultas,
        'user': request.user,
    })

# Registrar paciente
@login_required
def patient_create_view(request):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente registrado correctamente.')
            return redirect('reception:consultation_list')
    else:
        form = PatientForm()
    return render(request, 'reception/patient_form.html', {
        'form': form,
        'user': request.user,
    })

# Registrar consulta
@login_required
def consultation_create_view(request):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            # Asignar el orden automáticamente según el turno y fecha
            mismo_turno = Consultation.objects.filter(
                date=consulta.date,
                shift=consulta.shift,
                doctor=consulta.doctor
            ).count()
            consulta.order = mismo_turno + 1
            consulta.save()
            messages.success(request, 'Consulta agendada correctamente.')
            return redirect('reception:consultation_list')
    else:
        form = ConsultationForm()
    return render(request, 'reception/consultation_form.html', {
        'form': form,
        'user': request.user,
    })


@login_required
def consultation_edit_view(request, pk):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    consulta = get_object_or_404(Consultation, pk=pk)
    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consulta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consulta actualizada correctamente.')
            return redirect('reception:consultation_list')
    else:
        form = ConsultationForm(instance=consulta)
    return render(request, 'reception/consultation_form.html', {
        'form': form,
        'user': request.user,
    })

# Eliminar consulta
@login_required
def consultation_delete_view(request, pk):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    consulta = get_object_or_404(Consultation, pk=pk)
    if request.method == 'POST':
        consulta.delete()
        messages.success(request, 'Consulta eliminada correctamente.')
        return redirect('reception:consultation_list')
    return render(request, 'reception/consultation_confirm_delete.html', {
        'object': consulta,
        'user': request.user,
    })

@login_required
def reception_profile_view(request):
    """Vista del perfil"""
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    
    updated_profile_successfully = False
    updated_password_successfully = False
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            # Actualizar información del perfil
            user = request.user
            user.first_name = request.POST.get('user_firstname', user.first_name)
            user.last_name = request.POST.get('user_lastname', user.last_name)
            user.email = request.POST.get('user_email', user.email)
            user.username = request.POST.get('username', user.username)
            
            # Manejar archivo de imagen si se subió
            if 'profile_pic' in request.FILES:
                user.profile_avatar = request.FILES['profile_pic']
            
            try:
                user.save()
                updated_profile_successfully = True
                messages.success(request, 'Perfil actualizado exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al actualizar el perfil: {str(e)}')
        
        elif 'update_password' in request.POST:
            # Cambiar contraseña
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')
            
            if not request.user.check_password(current_password):
                messages.error(request, 'La contraseña actual es incorrecta.')
            elif new_password != confirm_new_password:
                messages.error(request, 'Las nuevas contraseñas no coinciden.')
            elif len(new_password) < 8:
                messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
            else:
                try:
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)  # Mantener la sesión activa
                    updated_password_successfully = True
                    messages.success(request, 'Contraseña cambiada exitosamente.')
                except Exception as e:
                    messages.error(request, f'Error al cambiar la contraseña: {str(e)}')
    
    context = {
        'updated_profile_successfully': updated_profile_successfully,
        'updated_password_successfully': updated_password_successfully,
    }
    
    return render(request, 'reception/profile.html', context)
