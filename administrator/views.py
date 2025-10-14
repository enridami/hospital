from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.http import JsonResponse
from django.db import transaction
from users.models import Users, Doctor, Administrator, Receptions, Specialty, Patient, DoctorSchedule
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Permission
from datetime import datetime
import re

# Create your views here.

@login_required
def admin_dashboard_view(request):
    """Dashboard específico para administradores - PROTEGIDO"""
    # Primera protección: @login_required
    # Segunda protección: verificar que sea administrador
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    
    admin = request.user.administrator
    return render(request, 'admin_backup/admin_dashboard.html', {
        'user': request.user,
        'administrator': admin,
    })


# Acciones del dashboard de Admnistrador
@login_required
def admin_dashboard_view(request):
    """Vista del dashboard para administradores"""
    # Verificar que el usuario sea administrador
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos para acceder al panel de administración.')
        return redirect('dashboard')
    
    # Obtener estadísticas
    from users.models import Users, Doctor, Administrator, Receptions, Patient
    
    # Contar usuarios por tipo
    total_users = Users.objects.count()
    total_doctors = Users.objects.filter(is_doctor=True).count()
    total_staff = Administrator.objects.count() + Receptions.objects.count()
    total_patients = Patient.objects.count()
    
    # Usuarios recientes (últimos 10)
    recent_users = Users.objects.order_by('-date_joined')[:10]
    
    # Calcular porcentajes para las barras de progreso
    if total_users > 0:
        doctors_percentage = round((total_doctors / total_users) * 100, 1)
        admin_count = Administrator.objects.count()
        reception_count = Receptions.objects.count()
        admin_percentage = round((admin_count / total_users) * 100, 1)
        staff_percentage = round((reception_count / total_users) * 100, 1)
    else:
        doctors_percentage = admin_percentage = staff_percentage = 0
    
    context = {
        'total_users': total_users,
        'total_doctors': total_doctors,
        'total_staff': total_staff,
        'total_patients': total_patients,
        'recent_users': recent_users,
        'doctors_percentage': doctors_percentage,
        'admin_percentage': admin_percentage,
        'staff_percentage': staff_percentage,
    }
    
    return render(request, 'admin_backup/admin_dashboard.html', context)


#Listar usuarios
@login_required
def admin_users_list(request):
    """Lista todos los usuarios"""
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    users = Users.objects.all().order_by('-date_joined')

    context = {
        'users': users,
        'total_users': users.count()
    }

    return render(request, 'admin_backup/users_list.html', context)


# Crear usuario desde Acciones rapidas

@login_required
def admin_create_user(request):
    """Crear nuevo usuario con validaciones robustas"""
    if not hasattr(request.user, 'administrator') or not request.user.has_perm('users.add_users'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    specialties = Specialty.objects.all().order_by('name')
    errores = []

    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', '')
        specialty_id = request.POST.get('specialty', '')
        bio = request.POST.get('bio', '').strip()
        profile_pic = request.FILES.get('profile_avatar')

        ### VALIDACIONES ###
        
        # Validación de campos obligatorios
        if not username or not email or not first_name or not last_name or not password or not role:
            errores.append("Todos los campos básicos son obligatorios.")

        # Validación de email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errores.append("El correo electrónico no es válido.")

        # Validación de contraseña segura
        if len(password) < 8 or password.isdigit() or password.isalpha():
            errores.append("La contraseña debe tener al menos 8 caracteres y contener letras y números.")

        # Validación de username único y sin espacios
        if " " in username:
            errores.append("El nombre de usuario no debe contener espacios.")
        if Users.objects.filter(username=username).exists():
            errores.append("El nombre de usuario ya está registrado.")

        # Validación de email único
        if Users.objects.filter(email=email).exists():
            errores.append("El correo ya está registrado.")

        # Validaciones específicas para doctor
        if role == 'doctor':
            if not specialty_id:
                errores.append("Debes seleccionar una especialidad para el doctor.")
            if not bio or len(bio) < 10:
                errores.append("La biografía profesional es obligatoria y debe tener al menos 10 caracteres.")

        # Validaciones para imagen de perfil
        if profile_pic:
            if not profile_pic.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                errores.append("La imagen de perfil debe ser JPG, PNG o GIF.")
            if profile_pic.size > 2 * 1024 * 1024:
                errores.append("La imagen de perfil no debe superar los 2MB.")
 

         

        # Validaciones para paciente
        if role == 'patient':
            phone = request.POST.get('phone', '').strip()
            birthday = request.POST.get('birthday', '').strip()
            identification_type = request.POST.get('identification_type', '').strip()
            identification_number = request.POST.get('identification_number', '').strip()
            address_line = request.POST.get('address_line', '').strip()
            city = request.POST.get('city', '').strip()
            emergency_contact_name = request.POST.get('emergency_contact_name', '').strip()
            emergency_contact_phone = request.POST.get('emergency_contact_phone', '').strip()

            # Teléfono válido (10-15 dígitos)
            if not re.match(r'^\+?\d{10,15}$', phone):
                errores.append("El teléfono debe tener entre 10 y 15 dígitos.")

            # Fecha de nacimiento válida (no futura)
             
            try:
                fecha_nac = datetime.strptime(birthday, "%Y-%m-%d")
                if fecha_nac > datetime.now():
                    errores.append("La fecha de nacimiento no puede ser futura.")
            except Exception:
                errores.append("La fecha de nacimiento es inválida.")

            # Número de identificación único
            if not identification_number:
                errores.append("El número de identificación es obligatorio.")
            elif Patient.objects.filter(identification_number=identification_number).exists():
                errores.append("El número de identificación ya está registrado.")

            # Dirección y ciudad obligatorias
            if not address_line:
                errores.append("La dirección es obligatoria.")
            if not city:
                errores.append("La ciudad es obligatoria.")

            # Contacto de emergencia obligatorio
            if not emergency_contact_name or not emergency_contact_phone:
                errores.append("El nombre y teléfono de contacto de emergencia son obligatorios.")
            elif not re.match(r'^\+?\d{10,15}$', emergency_contact_phone):
                errores.append("El teléfono de emergencia debe tener entre 10 y 15 dígitos.")


        print("---- DEPURACIÓN: POST DATA ----")
        for key, value in request.POST.items():
            print(f"{key}: {value}")
        print("---- DEPURACIÓN: FILES ----")
        for key, value in request.FILES.items():
            print(f"{key}: {value}")


        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'admin_backup/create_user.html', {'specialties': specialties})
        
        print("Errores detectados:", errores)

        try:
            with transaction.atomic():
                # Crear usuario
                print("Creando usuario...")
                user = Users.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                print("Usuario creado:", user)
                # Guardar imagen de perfil si se subió
                if profile_pic:
                    user.profile_avatar = profile_pic
                    user.save()
                    print("Imagen de perfil guardada.")
                
                # Asignar rol según selección
                if role == 'doctor':
                    user.is_doctor = True
                    user.save()
                    specialty = None
                    if specialty_id:
                        specialty = Specialty.objects.get(id=specialty_id)
                    Doctor.objects.create(user=user, specialty=specialty, bio=bio)
                elif role == 'admin':
                    print("Creando perfil de administrador...")
                    Administrator.objects.create(user=user)
                elif role == 'reception':
                    print("Creando perfil de recepcionista...")
                    Receptions.objects.create(user=user)
                elif role == 'patient':
                    print("Creando perfil de paciente...")
                    Patient.objects.create(
                        user=user,
                        phone=phone,
                        date_of_birth=birthday,
                        identification_type=identification_type,
                        identification_number=identification_number,
                        address_line=address_line,
                        city=city,
                        emergency_contact_name=emergency_contact_name,
                        emergency_contact_phone=emergency_contact_phone,
                    )
                print("Usuario y perfil creados correctamente.")
                messages.success(request, f'Usuario {user.get_full_name()} creado exitosamente.')
                return redirect('admin_users_list')
                
        except Exception as e:
            print("EXCEPCIÓN:", str(e))
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    return render(request, 'admin_backup/create_user.html', {'specialties': specialties})


# Crear doctor desde Acciones rapidas
@login_required
def admin_create_doctor(request):
    """Crear nuevo doctor y asignar horarios"""
    if not hasattr(request.user, 'administrator') or not request.user.has_perm('users.add_users'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        specialty_id = request.POST.get('specialty')
        bio = request.POST.get('bio', '')

        # Arrays de horarios y consultorios
        horario_days = request.POST.getlist('horario_day[]')
        horario_starts = request.POST.getlist('horario_start[]')
        horario_ends = request.POST.getlist('horario_end[]')
        horario_consultorios = request.POST.getlist('horario_consultorio[]')

        errores = []

        # Validación de contraseñas
        if password != request.POST.get('conf_password'):
            errores.append("Las contraseñas no coinciden.")
        if len(password) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres.")

        # Validación de email único
        if Users.objects.filter(email=email).exists():
            errores.append("El correo ya está registrado.")

        # Validación de nombre de usuario único
        if Users.objects.filter(username=username).exists():
            errores.append("El nombre de usuario ya está registrado.")

        # Validación de horarios
        for i in range(len(horario_days)):
            start = horario_starts[i]
            end = horario_ends[i]
            if start >= end:
                errores.append(f"En el horario {i+1}, la hora de inicio debe ser menor que la de fin.")
           

        # Validación de solapamiento de horarios para evitar que un doctor tenga dos turnos que se crucen el mismo día
        for i in range(len(horario_days)):
            for j in range(i + 1, len(horario_days)):
                if horario_days[i] == horario_days[j]:
                    start_i = horario_starts[i]
                    end_i = horario_ends[i]
                    start_j = horario_starts[j]
                    end_j = horario_ends[j]
                    # Si se solapan
                    if (start_i < end_j) and (end_i > start_j):
                        errores.append(
                            f"Los horarios {i+1} y {j+1} se solapan el día {horario_days[i]}."
                        )

        # Validación de consultorio repetido en el mismo horario
        for i in range(len(horario_days)):
            for j in range(i + 1, len(horario_days)):
                if (
                    horario_days[i] == horario_days[j] and
                    horario_starts[i] == horario_starts[j] and
                    horario_ends[i] == horario_ends[j] and
                    horario_consultorios[i].strip().lower() == horario_consultorios[j].strip().lower()
                ):
                    errores.append(
                        f"El consultorio '{horario_consultorios[i]}' está repetido en el mismo horario ({horario_days[i]}, {horario_starts[i]} - {horario_ends[i]})."
                    )



        if errores:
            for error in errores:
                messages.error(request, error)
            specialties = Specialty.objects.all()
            context = {'specialties': specialties}
            return render(request, 'admin_backup/create_doctor.html', context)
        
        
        try:
            with transaction.atomic():
                # Crear usuario
                user = Users.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    is_doctor=True
                )
                
                # Crear perfil de doctor
                specialty = None
                if specialty_id:
                    specialty = Specialty.objects.get(id=specialty_id)
                
                doctor = Doctor.objects.create(
                    user=user,
                    specialty=specialty,
                    bio=bio
                )

                # Crear horarios del doctor
                for day, start, end, consultorio in zip(horario_days, horario_starts, horario_ends, horario_consultorios):
                    if day and start and end and consultorio:
                        DoctorSchedule.objects.create(
                            doctor=doctor,
                            day=day,
                            start_time=start,
                            end_time=end,
                            consultorio=consultorio
                        )
                
                messages.success(request, f'Doctor {user.get_full_name()} creado exitosamente con horarios asignados.')
                return redirect('admin_users_list')
                
        except Exception as e:
            messages.error(request, f'Error al crear doctor: {str(e)}')
    
    specialties = Specialty.objects.all()
    context = {'specialties': specialties}
    return render(request, 'admin_backup/create_doctor.html', context)

# Crear personal desde Acciones rapidas
@login_required
def admin_create_staff(request):
    """Crear personal administrativo"""
    if not hasattr(request.user, 'administrator') or not request.user.has_perm('users.add_users'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = request.POST.get('role')  # 'admin' o 'reception'
        
        try:
            with transaction.atomic():
                # Crear usuario
                user = Users.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                
                # Crear perfil según rol
                if role == 'admin':
                    Administrator.objects.create(user=user)
                elif role == 'reception':
                    Receptions.objects.create(user=user)
                
                messages.success(request, f'Personal {user.get_full_name()} creado exitosamente.')
                return redirect('admin_users_list')
                
        except Exception as e:
            messages.error(request, f'Error al crear personal: {str(e)}')
    
    return render(request, 'admin_backup/create_staff.html')


# Acciones desde la tabla USUARIOS RECIENTES
@login_required
def admin_edit_user(request, user_id):
    """Editar usuario"""
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    user = get_object_or_404(Users, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        messages.success(request, f'Usuario {user.get_full_name()} actualizado.')
        return redirect('admin_users_list')
    
    context = {'user_to_edit': user}
    return render(request, 'admin_backup/edit_user.html', context)


# Boton para cambiar estado de usuarios
@login_required
@require_POST
def admin_toggle_user_status(request, user_id):
    """Cambiar estado activo/inactivo del usuario (AJAX)"""
    if not hasattr(request.user, 'administrator'):
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    try:
        user = get_object_or_404(Users, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        status = 'activado' if user.is_active else 'desactivado'
        return JsonResponse({
            'success': True, 
            'message': f'Usuario {status} exitosamente.',
            'new_status': user.is_active
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

@login_required
def admin_profile_view(request):
    """Vista del perfil del administrador"""
    if not hasattr(request.user, 'administrator'):
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
    
    return render(request, 'admin_backup/admin_profile.html', context)



# Asignar Roles
@login_required
def admin_assign_role(request, user_id):
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')

    user = get_object_or_404(Users, id=user_id)
    specialties = Specialty.objects.all()
    if request.method == 'POST':
        role = request.POST.get('role')
        specialty_id = request.POST.get('specialty')
        # Limpia roles previos
        user.is_doctor = False
        Administrator.objects.filter(user=user).delete()
        Receptions.objects.filter(user=user).delete()
        Doctor.objects.filter(user=user).delete()
        # Asigna nuevo rol
        if role == 'doctor':
            user.is_doctor = True
            user.save()
            specialty = Specialty.objects.get(id=specialty_id) if specialty_id else None
            Doctor.objects.create(user=user, specialty=specialty)
        elif role == 'admin':
            Administrator.objects.get_or_create(user=user)
        elif role == 'reception':
            Receptions.objects.get_or_create(user=user)
        user.save()
        messages.success(request, f'Rol asignado correctamente a {user.username}.')
        return redirect('admin_users_list')
    return render(request, 'admin_backup/assign_role.html', {'user': user, 'specialties': specialties})

@login_required
def admin_select_user_for_role(request):
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    users = Users.objects.all().order_by('username')
    return render(request, 'admin_backup/select_user_for_role.html', {'users': users})


# Permisos
@login_required
def admin_permissions_list(request):
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    User = get_user_model()
    users = User.objects.all().order_by('username')
    perms = Permission.objects.all().order_by('name')
    return render(request, 'admin_backup/permissions_list.html', {'users': users, 'perms': perms})



# Eliminar usuario
@login_required
@require_POST
def admin_delete_user(request, user_id):
    if not hasattr(request.user, 'administrator'):
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    try:
        user = get_object_or_404(Users, id=user_id)
        user.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

# Asignar permisos a usuario
@login_required
def assign_permission(request):
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        perm_id = request.POST.get('perm_id')
        action = request.POST.get('action')
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        perm = Permission.objects.get(pk=perm_id)
        if action == 'add':
            user.user_permissions.add(perm)
            messages.success(request, 'Permiso asignado correctamente.')
        elif action == 'remove':
            user.user_permissions.remove(perm)
            messages.success(request, 'Permiso removido correctamente.')
        return redirect('admin_permissions_list')
    return redirect('admin_permissions_list')