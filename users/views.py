from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Obtener el modelo de usuario personalizado
Users = get_user_model()

def login_view(request):
    """Vista para manejar el login de usuarios"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autenticar usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect a dashboard general para todos
            return redirect('dashboard')    
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
   
    return render(request, 'users/login.html')

# Dashboards específicos con doble protección de seguridad
@login_required
def dashboard_view(request):
    """Vista que redirecciona al dashboard especifico según el rol"""
    user = request.user

    if hasattr(user, 'doctor'):
        return redirect('doctor_dashboard')
    elif hasattr(user, 'receptions'):
        return redirect('reception_dashboard')
    elif hasattr(user, 'administrator'):
        return redirect('admin_dashboard')
    else:
        return render(request, 'users/dashboard.html', {
            'user': user,
            'user_type': 'Usuario sin rol',
            'specialty': None
        })


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
def reception_dashboard_view(request):
    """Dashboard específico para recepcionistas - PROTEGIDO"""
    # Primera protección: @login_required
    
    # Segunda protección: verificar que sea recepcionista
    if not hasattr(request.user, 'receptions'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    
    return render(request, 'reception/reception_dashboard.html', {
        'user': request.user,
    })

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

@login_required(login_url='/login/')
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect('login')


# Acciones del dashboard de Admnistrador
@login_required
def admin_dashboard_view(request):
    """Vista del dashboard para administradores"""
    # Verificar que el usuario sea administrador
    if not hasattr(request.user, 'administrator'):
        messages.error(request, 'No tienes permisos para acceder al panel de administración.')
        return redirect('dashboard')
    
    # Obtener estadísticas
    from .models import Users, Doctor, Administrator, Receptions, Patient
    
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