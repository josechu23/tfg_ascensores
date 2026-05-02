"""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología 
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

diagnostico/urls.py ─ Define todas las URLs de la aplicación de diagnóstico.

"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # Autenticación

    path(
        'login/',
        auth_views.LoginView.as_view(template_name='diagnostico/login.html'),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # Ascensores

    # Listado de ascensores asignados al técnico autenticado (UC01).
    path(
        'ascensores/',
        views.ascensor_list,
        name='ascensor_list'
    ),

    # Flujo de diagnóstico

    path(
        'ascensores/<int:ascensor_id>/sintomas/',
        views.sintomas_form,
        name='sintomas_form'
    ),

    # Resultado del diagnóstico generado por el motor de inferencia (UC03).
    path(
        'intervencion/<int:intervencion_id>/diagnostico/',
        views.diagnostico_resultado,
        name='diagnostico_resultado'
    ),

    # Intervención

    path(
        'intervencion/<int:intervencion_id>/registrar/',
        views.intervencion_registrar,
        name='intervencion_registrar'
    ),

    # Historial de intervenciones de un ascensor concreto (UC04).
    path(
        'ascensores/<int:ascensor_id>/historial/',
        views.historial_ascensor,
        name='historial_ascensor'
    ),

    # Generación del parte de trabajo de la intervención de mantenimiento correctivo en formato PDF (UC06).
    path(
    'intervencion/<int:intervencion_id>/pdf/',
    views.descargar_pdf,
    name='descargar_pdf'
),
]
