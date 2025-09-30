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
        return render(request, 'users/dashboard.html'), {
            'user': user,
            'user_type': 'Usuario sin rol',
            'specialty': None
        }


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
    return render(request, 'admin/admin_dashboard.html', {
        'user': request.user,
        'administrator': admin,
    })

@login_required(login_url='/login/')
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect('login')


