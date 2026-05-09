import json
import logging
from .models import Regla, Intervencion

logger = logging.getLogger(__name__)


def obtener_diagnostico(sintomas_ids, ascensor_id):
    sintomas_observados = set(sintomas_ids)

    if not sintomas_observados:
        return []

    reglas_activas = Regla.objects.filter(activa=True).prefetch_related('sintomas_requeridos')

    resultados = []
    for regla in reglas_activas:
        requeridos = set(regla.sintomas_requeridos.values_list('pk', flat=True))
        if not requeridos.issubset(sintomas_observados):
            continue

        pasos = [p.strip() for p in regla.pasos_comprobacion.split('\n') if p.strip()]

        resultados.append({
            'causa':            regla.causa_probable,
            'criticidad':       regla.criticidad,
            'criticidad_label': regla.get_criticidad_display(),
            'peso_final':       regla.peso_base,
            'pasos':            pasos,
            'regla_id':         regla.pk,
        })

    if not resultados:
        return []

    # Ajustar pesos según el historial del ascensor concreto
    historial = (
        Intervencion.objects
        .filter(ascensor_id=ascensor_id, resultado='resuelto')
        .exclude(causa_confirmada='')
        .order_by('-fecha_inicio')[:20]
    )

    frecuencia = {}
    for intervencion in historial:
        causa = intervencion.causa_confirmada.strip()
        if causa:
            frecuencia[causa] = frecuencia.get(causa, 0) + 1

    for r in resultados:
        veces = frecuencia.get(r['causa'], 0)
        if veces > 0:
            r['peso_final'] = round(r['peso_final'] + veces * 0.2, 2)

    resultados.sort(key=lambda x: x['peso_final'], reverse=True)
    return resultados


def serializar_diagnostico(resultados):
    return json.dumps(resultados, ensure_ascii=False)


def deserializar_diagnostico(diagnostico_json):
    if not diagnostico_json:
        return []
    try:
        return json.loads(diagnostico_json)
    except json.JSONDecodeError:
        logger.error('No se pudo deserializar el diagnóstico guardado')
        return []
