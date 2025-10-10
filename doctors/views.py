from django.shortcuts import render, redirect
from users.models import Doctor
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Consultation, Patient, Doctor
from django.shortcuts import get_object_or_404

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


@login_required
def doctor_profile_view(request):
    updated_profile_successfully = False
    updated_password_successfully = False

    if not hasattr(request.user, 'doctor'):
        messages.error(request, 'No tienes perfil de doctor.')
        return redirect('doctor_dashboard')

    doctor = request.user.doctor

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user = request.user
            user.first_name = request.POST.get('user_firstname', user.first_name)
            user.last_name = request.POST.get('user_lastname', user.last_name)
            user.email = request.POST.get('user_email', user.email)
            user.username = request.POST.get('username', user.username)
            if 'profile_pic' in request.FILES:
                user.profile_avatar = request.FILES['profile_pic']
            try:
                user.save()
                updated_profile_successfully = True
                messages.success(request, 'Perfil actualizado exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al actualizar el perfil: {str(e)}')
        elif 'update_password' in request.POST:
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
                    updated_password_successfully = True
                    messages.success(request, 'Contraseña cambiada exitosamente.')
                except Exception as e:
                    messages.error(request, f'Error al cambiar la contraseña: {str(e)}')

    context = {
        'updated_profile_successfully': updated_profile_successfully,
        'updated_password_successfully': updated_password_successfully,
        'doctor': doctor,
    }
    return render(request, 'doctors/profile.html', context)


@login_required
def doctor_patient_list_view(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        # Si el usuario no es doctor, muestra lista vacía o error
        return render(request, 'doctors/patient_list.html', {
            'patients': [],
            'ci_query': '',
            'user': request.user,
            'error': 'No tienes perfil de doctor.'
        })
    consultas = Consultation.objects.filter(doctor=doctor)
    pacientes = Patient.objects.filter(consultation__in=consultas).distinct()
    query = request.GET.get('ci', '')
    if query:
        pacientes = pacientes.filter(identification_number__icontains=query)
    return render(request, 'doctors/patient_list.html', {
        'patients': pacientes,
        'ci_query': query,
        'user': request.user,
    })


@login_required
def change_consultation_status_view(request, consultation_id):
    consulta = get_object_or_404(Consultation, id=consultation_id, doctor__user=request.user)
    if request.method == "POST":
        nuevo_estado = request.POST.get("nuevo_estado")
        if nuevo_estado in dict(Consultation.status_choices).keys():
            consulta.status = nuevo_estado
            consulta.save()
            messages.success(request, f"Estado cambiado a {consulta.get_status_display()}.")
        else:
            messages.error(request, "Estado inválido.")
    return redirect('doctor_patient_list')