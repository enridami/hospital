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
            
            return redirect('dashboard')  # URL temporal hasta adaptar la funcionalidad comentada abajo


            # Redireccionar según el tipo de usuario
            #if hasattr(user, 'is_doctor') and user.is_doctor:
                #return redirect('doctor_dashboard')  # Cambiar por tu URL de dashboard doctor
            #else:
                #return redirect('patient_dashboard')  # Cambiar por tu URL de dashboard paciente
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
    return render(request, 'users/dashboard.html', {'user': request.user})

