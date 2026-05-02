"""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología 
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

diagnostico/views.py - Define las vistas de la aplicación de diagnóstico.
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse

from .models import Ascensor, Sintoma, Subsistema, Intervencion
from .inference_engine import (
    obtener_diagnostico,
    serializar_diagnostico,
    deserializar_diagnostico,
)


# UC01: Listado de ascensores

@login_required
def ascensor_list(request):

    es_senior = (
        request.user.is_superuser or
        (hasattr(request.user, 'perfil') and request.user.perfil.es_tecnico_senior())
    )

    if es_senior:

        ascensores = Ascensor.objects.filter(activo=True)
    else:

        ascensores = Ascensor.objects.filter(
            tecnicos=request.user,
            activo=True
        )

    context = {
        'ascensores': ascensores,
        'es_senior': es_senior,  
    }
    return render(request, 'diagnostico/ascensor_list.html', context)


# UC02: Formulario de síntomas

@login_required
def sintomas_form(request, ascensor_id):

    ascensor = get_object_or_404(Ascensor, pk=ascensor_id, activo=True)

    subsistemas = Subsistema.objects.prefetch_related(
        'sintomas'
    ).filter(
        sintomas__activo=True
    ).distinct()

    if request.method == 'POST':

        sintomas_ids_str = request.POST.getlist('sintomas')

        sintomas_ids = [int(sid) for sid in sintomas_ids_str]

        if not sintomas_ids:
            messages.warning(
                request,
                'Por favor, selecciona al menos un síntoma antes de continuar.'
            )
            return redirect('sintomas_form', ascensor_id=ascensor_id)

        # Ejecutar el motor de inferencia
        resultados = obtener_diagnostico(
            sintomas_ids=sintomas_ids,
            ascensor_id=ascensor_id
        )

        # Crear la intervención en la base de datos
        intervencion = Intervencion.objects.create(
            ascensor=ascensor,
            tecnico=request.user,
            diagnostico_generado=serializar_diagnostico(resultados),
        )

        # Asociar los síntomas seleccionados a la intervención.
        sintomas_seleccionados = Sintoma.objects.filter(pk__in=sintomas_ids)
        intervencion.sintomas_registrados.set(sintomas_seleccionados)

        return redirect('diagnostico_resultado', intervencion_id=intervencion.pk)

    ultimas_intervenciones = Intervencion.objects.filter(
        ascensor=ascensor
    ).order_by('-fecha_inicio')[:3]

    context = {
        'ascensor':               ascensor,
        'subsistemas':            subsistemas,
        'ultimas_intervenciones': ultimas_intervenciones,
    }
    return render(request, 'diagnostico/sintomas_form.html', context)


# UC03: Resultado del diagnóstico

@login_required
def diagnostico_resultado(request, intervencion_id):

    intervencion = get_object_or_404(Intervencion, pk=intervencion_id)

    resultados = deserializar_diagnostico(intervencion.diagnostico_generado)

    context = {
        'intervencion':   intervencion,
        'ascensor':       intervencion.ascensor,
        'resultados':     resultados,
        'hay_resultados': len(resultados) > 0,
    }
    return render(request, 'diagnostico/diagnostico_resultado.html', context)


# UC05: Registro de intervención correctiva

@login_required
def intervencion_registrar(request, intervencion_id):

    intervencion = get_object_or_404(Intervencion, pk=intervencion_id)

    resultados = deserializar_diagnostico(intervencion.diagnostico_generado)

    if request.method == 'POST':
        causa_confirmada  = request.POST.get('causa_confirmada', '').strip()
        accion_correctiva = request.POST.get('accion_correctiva', '').strip()
        observaciones     = request.POST.get('observaciones', '').strip()
        resultado         = request.POST.get('resultado', 'resuelto')

        if not accion_correctiva:
            messages.error(
                request,
                'Por favor, describe la acción correctiva aplicada.'
            )
            return render(request, 'diagnostico/intervencion_form.html', {
                'intervencion': intervencion,
                'ascensor':     intervencion.ascensor,
                'resultados':   resultados,
                'resultado_choices': Intervencion.RESULTADO_CHOICES,
            })

        intervencion.causa_confirmada  = causa_confirmada
        intervencion.accion_correctiva = accion_correctiva
        intervencion.observaciones     = observaciones
        intervencion.resultado         = resultado
        intervencion.fecha_fin         = timezone.now()
        intervencion.save()

        messages.success(
            request,
            f'Intervención #{intervencion.pk} registrada correctamente.'
        )

        return redirect('historial_ascensor', ascensor_id=intervencion.ascensor.pk)

    context = {
        'intervencion':      intervencion,
        'ascensor':          intervencion.ascensor,
        'resultados':        resultados,
        'resultado_choices': Intervencion.RESULTADO_CHOICES,
    }
    return render(request, 'diagnostico/intervencion_form.html', context)


# UC04: Historial de intervenciones

@login_required
def historial_ascensor(request, ascensor_id):

    ascensor = get_object_or_404(Ascensor, pk=ascensor_id, activo=True)

    intervenciones = Intervencion.objects.filter(
        ascensor=ascensor
    ).select_related(
        'tecnico'
    ).order_by('-fecha_inicio')

    context = {
        'ascensor':       ascensor,
        'intervenciones': intervenciones,
    }
    return render(request, 'diagnostico/historial.html', context)


# UC06: Descargar parte de trabajo en PDF

@login_required
def descargar_pdf(request, intervencion_id):

    intervencion = get_object_or_404(Intervencion, pk=intervencion_id)

    pdf_bytes = generar_parte_trabajo(intervencion)

    nombre_fichero = f'parte_trabajo_intervencion_{intervencion.pk}.pdf'

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_fichero}"'
    return response
