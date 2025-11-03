from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Consultation, Patient, Doctor, Specialty, DoctorSchedule
from .forms import PatientForm, ConsultationForm
from datetime import datetime, timedelta, date, time

# Dashboard principal
@login_required
def reception_dashboard_view(request):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    pacientes_count = Patient.objects.count()
    doctores_count = Doctor.objects.count()
    consultas_count = Consultation.objects.count()
    consultas_hoy = Consultation.objects.filter(date__exact=date.today()).count()

    return render(request, 'reception/reception_dashboard.html', {
        'user': request.user,
        'pacientes_count': pacientes_count,
        'doctores_count': doctores_count,
        'consultas_count': consultas_count,
        'consultas_hoy': consultas_hoy,
    })

# Listar consultas
@login_required
def consultation_list_view(request):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    consultas = Consultation.objects.exclude(status="ATENDIDO").order_by('date', 'shift', 'order')
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
    especialidades = Specialty.objects.all()
    especialidad_id = request.POST.get('especialidad') or request.GET.get('especialidad')
    doctores = Doctor.objects.none()
    consultorio_asignado = None

    if especialidad_id:
        doctores = Doctor.objects.filter(specialty_id=especialidad_id)

    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')

    ci_query = request.GET.get('ci_query', '')
    paciente_encontrado = None
    if ci_query:
        paciente_encontrado = Patient.objects.filter(identification_number=ci_query).first()

    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        form.fields['doctor'].queryset = doctores
        if paciente_encontrado:
            form.instance.patient = paciente_encontrado
        else:
            messages.error(request, "Debes buscar y seleccionar un paciente antes de agendar la consulta.")
        if form.is_valid() and paciente_encontrado:
            consulta = form.save(commit=False)

            # Asignar el turno automáticamente si viene en el POST
            turno_auto = request.POST.get('turno_auto')
            if turno_auto:
                consulta.shift = turno_auto


            # Asignar consultorio automáticamente según el horario del doctor
            day_name = consulta.date.strftime('%A').upper()
            day_map = {
                'MONDAY': 'LUNES', 'TUESDAY': 'MARTES', 'WEDNESDAY': 'MIERCOLES',
                'THURSDAY': 'JUEVES', 'FRIDAY': 'VIERNES', 'SATURDAY': 'SABADO', 'SUNDAY': 'DOMINGO'
            }
            day = day_map.get(day_name, day_name)
            horario = DoctorSchedule.objects.filter(
                doctor=consulta.doctor,
                day=day,
                start_time__lte=consulta.time,
                end_time__gte=consulta.time
            ).first()
            if not horario:
                messages.error(request, "El doctor no está disponible en ese horario.")
            else:
                consulta.consultorio = horario.consultorio
                mismo_turno = Consultation.objects.filter(
                    date=consulta.date,
                    shift=consulta.shift,
                    doctor=consulta.doctor
                ).count()
                consulta.order = mismo_turno + 1
                consulta.save()
                messages.success(request, 'Consulta agendada correctamente.')
                return redirect('reception:consultation_list')
            
            if horario:
             consultorio_asignado = horario.consultorio

        elif not paciente_encontrado:
            pass
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = ConsultationForm()
        form.fields['doctor'].queryset = doctores

    return render(request, 'reception/consultation_form.html', {
        'form': form,
        'user': request.user,
        'ci_query': ci_query,
        'paciente_encontrado': paciente_encontrado,
        'especialidades': especialidades,
        'especialidad_id': especialidad_id,
        'consultorio_asignado': consultorio_asignado,
    })

# Editar consulta ya agendada
@login_required
def consultation_edit_view(request, pk):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')

    consulta = get_object_or_404(Consultation, pk=pk)
    especialidades = Specialty.objects.all()

    # Obtener especialidad seleccionada (por GET, POST o la actual de la consulta)
    especialidad_id = (
        request.POST.get('especialidad')
        or request.GET.get('especialidad')
        or (str(consulta.doctor.specialty.id) if consulta.doctor and consulta.doctor.specialty else '')
    )

    # Filtrar doctores según la especialidad seleccionada
    doctores = Doctor.objects.none()
    if especialidad_id:
        doctores = Doctor.objects.filter(specialty_id=especialidad_id)
    else:
        doctores = Doctor.objects.all()

    # Paciente y CI
    ci_query = consulta.patient.identification_number if consulta.patient else ''
    paciente_encontrado = consulta.patient if consulta.patient else None

    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consulta)
        form.fields['doctor'].queryset = doctores
        if form.is_valid():
            form.save()
            messages.success(request, 'Consulta actualizada correctamente.')
            return redirect('reception:consultation_list')
    else:
        form = ConsultationForm(instance=consulta)
        form.fields['doctor'].queryset = doctores

    return render(request, 'reception/consultation_form.html', {
        'form': form,
        'user': request.user,
        'ci_query': ci_query,
        'paciente_encontrado': paciente_encontrado,
        'especialidades': especialidades,
        'especialidad_id': especialidad_id,
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


@login_required
def patient_list_view(request):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    query = request.GET.get('ci', '')
    if query:
        pacientes = Patient.objects.filter(identification_number__icontains=query).order_by('-created_at')
    else:
        pacientes = Patient.objects.all().order_by('-created_at')
    return render(request, 'reception/patient_list.html', {
        'patients': pacientes,
        'user': request.user,
        'ci_query': query,
    })


@login_required
def patient_edit_view(request, pk):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    paciente = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente actualizado correctamente.')
            return redirect('reception:patient_list')
    else:
        form = PatientForm(instance=paciente)
    return render(request, 'reception/patient_edit.html', {
        'form': form,
        'user': request.user,
    })


# Eliminar paciente
@login_required
def patient_delete_view(request, pk):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    paciente = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente eliminado correctamente.')
        return redirect('reception:patient_list')
    return render(request, 'reception/patient_confirm_delete.html', {
        'object': paciente,
        'user': request.user,
    })


# Historial de consultas realizadas
@login_required
def consultation_history_view(request):
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    consultas = Consultation.objects.filter(status="ATENDIDO").order_by('-date', '-time')
    return render(request, 'reception/consultation_history.html', {
        'consultations': consultas,
        'user': request.user,
    })




@login_required
def doctor_schedule_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    horarios = DoctorSchedule.objects.filter(doctor=doctor).order_by('day', 'start_time')
    bloques_por_horario = []

    # Obtén la fecha seleccionada del parámetro GET
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha = datetime.today().date()
    else:
        fecha = datetime.today().date()


    # 1. Obtener el nombre del día en español (según tu modelo)
    dias_map = {
        0: 'LUNES', 1: 'MARTES', 2: 'MIERCOLES', 3: 'JUEVES',
        4: 'VIERNES', 5: 'SABADO', 6: 'DOMINGO'
    }
    dia_semana = dias_map[fecha.weekday()]

    # 2. Filtrar horarios solo para ese día
    horarios = DoctorSchedule.objects.filter(doctor=doctor, day=dia_semana).order_by('start_time')
    bloques_por_horario = []
        
    # Duración de cada consulta (en minutos)
    duracion_consulta = 30

    for horario in horarios:
        # Convierte start_time y end_time a datetime para operar
        inicio = datetime.combine(datetime.today(), horario.start_time)
        fin = datetime.combine(datetime.today(), horario.end_time)
        bloques = []
        actual = inicio
        while actual + timedelta(minutes=duracion_consulta) <= fin:
            bloque_inicio = actual.time()
            bloque_fin = (actual + timedelta(minutes=duracion_consulta)).time()
            # Verifica si ya hay una consulta agendada en ese bloque
            consulta_existente = Consultation.objects.filter(
                doctor=doctor,
                date=fecha,   
                time=bloque_inicio,
                consultorio=horario.consultorio
            ).exists()
            bloques.append({
                'dia': horario.day,
                'inicio': bloque_inicio.strftime('%H:%M'),
                'fin': bloque_fin.strftime('%H:%M'),
                'consultorio': horario.consultorio,
                'ocupado': consulta_existente
            })
            actual += timedelta(minutes=duracion_consulta)
        bloques_por_horario.append({
            'horario': horario,
            'bloques': bloques
        })     

    doctor_no_atiende = not horarios.exists()

    return render(request, 'reception/doctor_schedule_modal.html', {
        'doctor': doctor,
        'bloques_por_horario': bloques_por_horario,
        'doctor_no_atiende': doctor_no_atiende,
        'dia_semana': dia_semana,
    })

@login_required
def patient_detail(request,pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'reception/patient_detail.html', {'patient': patient})