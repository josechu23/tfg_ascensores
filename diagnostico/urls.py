from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='diagnostico/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('ascensores/', views.ascensor_list, name='ascensor_list'),
    path('ascensores/<int:ascensor_id>/sintomas/', views.sintomas_form, name='sintomas_form'),
    path('ascensores/<int:ascensor_id>/historial/', views.historial_ascensor, name='historial_ascensor'),

    path('intervencion/<int:intervencion_id>/diagnostico/', views.diagnostico_resultado, name='diagnostico_resultado'),
    path('intervencion/<int:intervencion_id>/registrar/', views.intervencion_registrar, name='intervencion_registrar'),
    path('intervencion/<int:intervencion_id>/pdf/', views.descargar_pdf, name='descargar_pdf'),
]
