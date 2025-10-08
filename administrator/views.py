from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.db import transaction
from users.models import Users, Doctor, Administrator, Receptions, Specialty, Patient
from django.views.decorators.http import require_POST
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
    """Crear nuevo usuario"""
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
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
                
                # Asignar rol según selección
                if role == 'doctor':
                    user.is_doctor = True
                    user.save()
                    # Crear perfil de doctor (necesitarás specialty)
                    Doctor.objects.create(user=user)
                elif role == 'admin':
                    Administrator.objects.create(user=user)
                elif role == 'reception':
                    Receptions.objects.create(user=user)
                
                messages.success(request, f'Usuario {user.get_full_name()} creado exitosamente.')
                return redirect('admin_users_list')
                
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    return render(request, 'admin_backup/create_user.html')


# Crear doctor desde Acciones rapidas
@login_required
def admin_create_doctor(request):
    """Crear nuevo doctor"""
    if not hasattr(request.user, 'administrator'):
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
                
                Doctor.objects.create(
                    user=user,
                    specialty=specialty,
                    bio=bio
                )
                
                messages.success(request, f'Doctor {user.get_full_name()} creado exitosamente.')
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
    if not hasattr(request.user, 'administrator'):
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