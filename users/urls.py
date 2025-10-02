from django.urls import path
from .views import login_view, logout_view, dashboard_view, doctor_dashboard_view, reception_dashboard_view, admin_dashboard_view
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', login_view, name='password-reset'),
    path('dashboard/', dashboard_view, name='dashboard'), # Dashboard general
    path('doctor-dashboard/', doctor_dashboard_view, name='doctor_dashboard'),
    path('reception-dashboard/', reception_dashboard_view, name='reception_dashboard'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('password-reset/', login_view, name='password-reset'), #temporal para que pueda recuperar contraseña
]

# Configuración para servir archivos estáticos en desarrollo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()

