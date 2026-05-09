import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse

from .models import Ascensor, Sintoma, Subsistema, Intervencion
from .inference_engine import obtener_diagnostico, serializar_diagnostico, deserializar_diagnostico
from .report_generator import generar_parte_trabajo


@login_required
def ascensor_list(request):
    es_senior = (
        request.user.is_superuser or
        (hasattr(request.user, 'perfil') and request.user.perfil.es_tecnico_senior())
    )

    if es_senior:
        ascensores = Ascensor.objects.filter(activo=True)
    else:
        ascensores = Ascensor.objects.filter(tecnicos=request.user, activo=True)

    return render(request, 'diagnostico/ascensor_list.html', {
        'ascensores': ascensores,
        'es_senior': es_senior,
    })


@login_required
def sintomas_form(request, ascensor_id):
    ascensor = get_object_or_404(Ascensor, pk=ascensor_id, activo=True)
    subsistemas = Subsistema.objects.prefetch_related('sintomas').filter(
        sintomas__activo=True
    ).distinct()

    if request.method == 'POST':
        sintomas_ids = [int(sid) for sid in request.POST.getlist('sintomas')]

        if not sintomas_ids:
            messages.warning(request, 'Selecciona al menos un síntoma antes de continuar.')
            return redirect('sintomas_form', ascensor_id=ascensor_id)

        resultados = obtener_diagnostico(sintomas_ids=sintomas_ids, ascensor_id=ascensor_id)

        intervencion = Intervencion.objects.create(
            ascensor=ascensor,
            tecnico=request.user,
            diagnostico_generado=serializar_diagnostico(resultados),
        )
        intervencion.sintomas_registrados.set(Sintoma.objects.filter(pk__in=sintomas_ids))

        return redirect('diagnostico_resultado', intervencion_id=intervencion.pk)

    ultimas = Intervencion.objects.filter(ascensor=ascensor).order_by('-fecha_inicio')[:3]

    return render(request, 'diagnostico/sintomas_form.html', {
        'ascensor': ascensor,
        'subsistemas': subsistemas,
        'ultimas_intervenciones': ultimas,
    })


@login_required
def diagnostico_resultado(request, intervencion_id):
    intervencion = get_object_or_404(Intervencion, pk=intervencion_id)
    resultados = deserializar_diagnostico(intervencion.diagnostico_generado)

    return render(request, 'diagnostico/diagnostico_resultado.html', {
        'intervencion': intervencion,
        'ascensor': intervencion.ascensor,
        'resultados': resultados,
        'hay_resultados': len(resultados) > 0,
    })


@login_required
def intervencion_registrar(request, intervencion_id):
    intervencion = get_object_or_404(Intervencion, pk=intervencion_id)
    resultados = deserializar_diagnostico(intervencion.diagnostico_generado)

    if request.method == 'POST':
        accion = request.POST.get('accion_correctiva', '').strip()

        if not accion:
            messages.error(request, 'Describe la acción correctiva aplicada.')
            return render(request, 'diagnostico/intervencion_form.html', {
                'intervencion': intervencion,
                'ascensor': intervencion.ascensor,
                'resultados': resultados,
                'resultado_choices': Intervencion.RESULTADO_CHOICES,
            })

        intervencion.causa_confirmada  = request.POST.get('causa_confirmada', '').strip()
        intervencion.accion_correctiva = accion
        intervencion.observaciones     = request.POST.get('observaciones', '').strip()
        intervencion.resultado         = request.POST.get('resultado', 'resuelto')
        intervencion.fecha_fin         = timezone.now()
        intervencion.save()

        messages.success(request, f'Intervención #{intervencion.pk} guardada.')
        return redirect('historial_ascensor', ascensor_id=intervencion.ascensor.pk)

    return render(request, 'diagnostico/intervencion_form.html', {
        'intervencion': intervencion,
        'ascensor': intervencion.ascensor,
        'resultados': resultados,
        'resultado_choices': Intervencion.RESULTADO_CHOICES,
    })


@login_required
def historial_ascensor(request, ascensor_id):
    ascensor = get_object_or_404(Ascensor, pk=ascensor_id, activo=True)
    intervenciones = (
        Intervencion.objects
        .filter(ascensor=ascensor)
        .select_related('tecnico')
        .order_by('-fecha_inicio')
    )

    return render(request, 'diagnostico/historial.html', {
        'ascensor': ascensor,
        'intervenciones': intervenciones,
    })


@login_required
def descargar_pdf(request, intervencion_id):
    intervencion = get_object_or_404(Intervencion, pk=intervencion_id)
    pdf_bytes = generar_parte_trabajo(intervencion)
    nombre = f'parte_{intervencion.pk}.pdf'

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return response
