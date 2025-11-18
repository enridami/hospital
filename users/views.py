from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Obtener el modelo de usuario personalizado
Users = get_user_model()

# Iniciar sesión
def login_view(request):
    """Vista para manejar el login de usuarios"""
    list(messages.get_messages(request))
    
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

    return render(request, 'users/login.html', context={})

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

# Cerrar sesión
@login_required(login_url='/login/')
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    list(messages.get_messages(request))
    return redirect('login')
