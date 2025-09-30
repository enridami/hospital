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
            
            # Detectar tipo de usuario
            if hasattr(user, 'doctor') and user.is_doctor:
                return redirect('doctor_dashboard')
            elif hasattr(user, 'receptions'):
                return redirect('reception_dashboard')
            elif hasattr(user, 'administrator'):
                return redirect('admin_dashboard')
            else:
                return render(request, 'users/dashboard.html')
            
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            
    return render(request, 'users/login.html')


@login_required(login_url='/login/')
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect('login')


# Vista temporal para dashboard  
@login_required
def dashboard_view(request):
    """Vista temporal de dashboard"""
    is_doctor_group = request.user.groups.filter(name='Doctor').exists()
    return render(request, 'users/dashboard.html', {
        'user': request.user,
        'is_doctor_group': is_doctor_group
    })

