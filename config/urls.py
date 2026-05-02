"""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología 
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

config/urls.py - fichero principal de enrutamiento
"""

from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include

urlpatterns = [
    # Accesible en http://127.0.0.1:8000/admin/
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/'), name='home'),
    path('', include('diagnostico.urls')),
]


