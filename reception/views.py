from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.
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


