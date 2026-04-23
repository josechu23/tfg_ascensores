"""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología 
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

inference_engine.py ─ Motor de inferencia del sistema experto.
"""

import json
import logging
from .models import Regla, Intervencion

logger = logging.getLogger('inference_engine')


def obtener_diagnostico(sintomas_ids, ascensor_id):


    # Paso 1: Convertir la lista de IDs a un conjunto (set)
    sintomas_observados = set(sintomas_ids)

    if not sintomas_observados:
        logger.warning('El motor fue invocado sin síntomas. Se devuelve lista vacía.')
        return []

    # Paso 2: Recuperar todas las reglas activas de la base de datos

    reglas_activas = (
        Regla.objects
        .filter(activa=True)
        .prefetch_related('sintomas_requeridos')
    )

    logger.debug(
        f'Motor iniciado. '
        f'Síntomas observados: {sintomas_observados}. '
        f'Reglas activas en BD: {reglas_activas.count()}'
    )

    #  Paso 3: Evaluar cada regla 
    resultados = []

    for regla in reglas_activas:

        sintomas_requeridos = set(
            regla.sintomas_requeridos.values_list('pk', flat=True)
        )

        if not sintomas_requeridos.issubset(sintomas_observados):
            continue

        logger.debug(
            f'Regla activada: "{regla.nombre}" '
            f'→ causa: "{regla.causa_probable}"'
        )

        pasos = [
            paso.strip()
            for paso in regla.pasos_comprobacion.split('\n')
            if paso.strip()
        ]

        resultados.append({
            'causa':            regla.causa_probable,
            'criticidad':       regla.criticidad,
            'criticidad_label': regla.get_criticidad_display(),
            'peso_final':       regla.peso_base,
            'pasos':            pasos,
            'regla_id':         regla.pk,
        })

    if not resultados:
        logger.info(
            f'Ninguna regla activada para los síntomas {sintomas_observados}.'
        )
        return []

    # Paso 4: Ajustar pesos con el historial del ascensor 

    historial = (
        Intervencion.objects
        .filter(
            ascensor_id=ascensor_id,
            resultado='resuelto'  
        )
        .exclude(
            causa_confirmada=''    
        )
        .order_by('-fecha_inicio')[:20] 
    )

    frecuencia_causas = {}
    for intervencion in historial:
        causa = intervencion.causa_confirmada.strip()
        if causa:
            frecuencia_causas[causa] = frecuencia_causas.get(causa, 0) + 1

    for resultado in resultados:
        causa = resultado['causa']
        veces_en_historial = frecuencia_causas.get(causa, 0)
        if veces_en_historial > 0:
            incremento = veces_en_historial * 0.2
            resultado['peso_final'] = round(resultado['peso_final'] + incremento, 2)
            logger.debug(
                f'Causa "{causa}" aparece {veces_en_historial}x en historial. '
                f'Peso ajustado: {resultado["peso_final"]}'
            )

    # Paso 5: Ordenar de mayor a menor peso 
    resultados.sort(key=lambda x: x['peso_final'], reverse=True)

    logger.info(
        f'Motor completado. {len(resultados)} causa(s) encontrada(s) '
        f'para ascensor ID={ascensor_id}.'
    )

    return resultados


def serializar_diagnostico(resultados):

    return json.dumps(resultados, ensure_ascii=False, indent=2)


def deserializar_diagnostico(diagnostico_json):


    if not diagnostico_json:
        return []

    try:
        return json.loads(diagnostico_json)
    except json.JSONDecodeError:

        logger.error(
            f'Error al deserializar diagnóstico JSON: '
            f'{diagnostico_json[:100]}...'
        )
        return []