"""
inference_engine.py
───────────────────
Motor de inferencia del sistema experto de diagnóstico de averías.

Implementa un algoritmo de encadenamiento hacia adelante (forward chaining):
dado un conjunto de síntomas observados por el técnico y el ascensor
sobre el que se interviene, recorre la base de conocimiento buscando
todas las reglas cuyas condiciones quedan satisfechas y devuelve
una lista ordenada de causas probables.

Este módulo es Python puro, completamente independiente de la capa web.
Puede ejecutarse y probarse desde la consola de Django sin necesidad
de abrir el navegador.

Funciones:
    obtener_diagnostico()      → ejecuta el motor y devuelve causas probables
    serializar_diagnostico()   → convierte el resultado a JSON para guardarlo en BD
    deserializar_diagnostico() → recupera el resultado desde el JSON almacenado en BD
"""

import json
import logging
from .models import Regla, Intervencion

# Logger para registrar eventos del motor en la consola durante el desarrollo.
# Los mensajes aparecen en la terminal con el prefijo 'inference_engine'.
# Niveles: DEBUG (detalle máximo), INFO (información general), WARNING, ERROR.
logger = logging.getLogger('inference_engine')


def obtener_diagnostico(sintomas_ids, ascensor_id):
    """
    Función principal del motor de inferencia.

    Dado un conjunto de síntomas seleccionados por el técnico y el
    ascensor sobre el que se interviene, devuelve una lista de causas
    probables ordenadas de mayor a menor probabilidad.

    Parámetros:
        sintomas_ids (list[int]):
            Lista de IDs (pk) de los síntomas que el técnico ha seleccionado.
            Ejemplo: [1, 2] significa que seleccionó los síntomas con ID 1 y 2.

        ascensor_id (int):
            ID (pk) del ascensor sobre el que se interviene.
            Se usa para consultar el historial y ajustar los pesos de probabilidad.

    Retorna:
        list[dict]: Lista de diccionarios ordenada de mayor a menor peso.
        Cada diccionario tiene esta estructura:
        {
            'causa':            str,   # Descripción de la causa probable
            'criticidad':       str,   # Valor interno: 'critico','urgente','diferible'
            'criticidad_label': str,   # Etiqueta legible: 'Crítico', 'Urgente', etc.
            'peso_final':       float, # Peso tras el ajuste por historial del ascensor
            'pasos':            list,  # Lista de strings con pasos de comprobación
            'regla_id':         int,   # ID de la regla que generó esta causa
        }

        Si no se activa ninguna regla devuelve una lista vacía: []
    """

    # ── Paso 1: Convertir la lista de IDs a un conjunto (set) ─────────────────
    # Un set permite comprobar si un elemento está contenido en él de forma
    # mucho más rápida que una lista, lo que acelera el motor cuando hay
    # muchas reglas en la base de conocimiento.
    # Ejemplo: sintomas_ids=[1,2] → sintomas_observados={1,2}
    sintomas_observados = set(sintomas_ids)

    # Si el técnico no seleccionó ningún síntoma no tiene sentido ejecutar
    # el motor. Devolvemos lista vacía inmediatamente.
    if not sintomas_observados:
        logger.warning('El motor fue invocado sin síntomas. Se devuelve lista vacía.')
        return []

    # ── Paso 2: Recuperar todas las reglas activas de la base de datos ─────────
    # prefetch_related('sintomas_requeridos') carga los síntomas de cada regla
    # en una sola consulta SQL adicional, evitando el problema N+1 de consultas
    # (sin esto Django haría una consulta por cada regla al acceder a sus síntomas,
    # lo que ralentizaría el motor con bases de conocimiento grandes).
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

    # ── Paso 3: Evaluar cada regla ─────────────────────────────────────────────
    # resultados acumulará los datos de todas las reglas que se activen.
    resultados = []

    for regla in reglas_activas:

        # Obtenemos el conjunto de IDs de síntomas que esta regla requiere.
        # values_list('pk', flat=True) devuelve solo los IDs, no objetos completos,
        # lo que es más eficiente en memoria.
        # Ejemplo: {1, 2} significa que la regla necesita los síntomas 1 y 2.
        sintomas_requeridos = set(
            regla.sintomas_requeridos.values_list('pk', flat=True)
        )

        # ── Condición IF de la regla IF-THEN ────────────────────────────────
        # Comprobamos si TODOS los síntomas requeridos por esta regla
        # están entre los síntomas que el técnico ha observado.
        # issubset() devuelve True si A ⊆ B (A está contenido en B).
        #
        # Ejemplo con síntomas observados = {1, 2, 7}:
        #   Regla requiere {1, 2}  → {1,2}.issubset({1,2,7}) = True  → ACTIVADA
        #   Regla requiere {1, 5}  → {1,5}.issubset({1,2,7}) = False → DESCARTADA
        if not sintomas_requeridos.issubset(sintomas_observados):
            # Esta regla no se activa porque falta algún síntoma requerido.
            continue

        # Si llegamos aquí la regla se ha activado.
        logger.debug(
            f'Regla activada: "{regla.nombre}" '
            f'→ causa: "{regla.causa_probable}"'
        )

        # Convertimos los pasos de comprobación de texto plano a lista de strings.
        # El campo pasos_comprobacion almacena un paso por línea.
        # split('\n') divide el texto por los saltos de línea.
        # El filtro 'if paso.strip()' elimina líneas vacías.
        pasos = [
            paso.strip()
            for paso in regla.pasos_comprobacion.split('\n')
            if paso.strip()
        ]

        # Añadimos esta causa a la lista de resultados con su peso base.
        # El peso se ajustará en el Paso 4 según el historial del ascensor.
        resultados.append({
            'causa':            regla.causa_probable,
            'criticidad':       regla.criticidad,
            'criticidad_label': regla.get_criticidad_display(),
            'peso_final':       regla.peso_base,
            'pasos':            pasos,
            'regla_id':         regla.pk,
        })

    # Si ninguna regla se ha activado devolvemos lista vacía.
    if not resultados:
        logger.info(
            f'Ninguna regla activada para los síntomas {sintomas_observados}.'
        )
        return []

    # ── Paso 4: Ajustar pesos con el historial del ascensor ───────────────────
    # Consultamos las últimas 20 intervenciones resueltas de este ascensor.
    # Limitamos a 20 para no ralentizar el sistema en instalaciones con mucho
    # historial. Las más recientes tienen más valor diagnóstico.
    historial = (
        Intervencion.objects
        .filter(
            ascensor_id=ascensor_id,  # Solo intervenciones de este ascensor
            resultado='resuelto'       # Solo intervenciones que se resolvieron
        )
        .exclude(
            causa_confirmada=''        # Ignoramos las sin causa registrada
        )
        .order_by('-fecha_inicio')[:20]  # Las 20 más recientes, de nueva a antigua
    )

    # Contamos cuántas veces ha aparecido cada causa confirmada en el historial.
    # Usamos un diccionario donde la clave es la causa y el valor es el contador.
    # Ejemplo: {'Operador de puertas defectuoso': 3, 'Cable desgastado': 1}
    frecuencia_causas = {}
    for intervencion in historial:
        causa = intervencion.causa_confirmada.strip()
        if causa:
            # dict.get(clave, valor_por_defecto) devuelve el valor actual
            # o 0 si la clave no existe todavía en el diccionario.
            frecuencia_causas[causa] = frecuencia_causas.get(causa, 0) + 1

    # Ajustamos el peso de cada causa activada en función de su frecuencia
    # histórica en este ascensor concreto.
    # Por cada aparición en el historial aumentamos el peso un 20% (factor 0.2).
    # Ejemplo: peso_base=2.5, la causa aparece 3 veces en historial
    #          → peso_final = 2.5 + (3 × 0.2) = 3.1
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

    # ── Paso 5: Ordenar de mayor a menor peso ──────────────────────────────────
    # La causa con mayor peso aparece primera en la lista,
    # que es lo que verá el técnico al consultar el diagnóstico.
    # reverse=True invierte el orden natural (ascendente) a descendente.
    resultados.sort(key=lambda x: x['peso_final'], reverse=True)

    logger.info(
        f'Motor completado. {len(resultados)} causa(s) encontrada(s) '
        f'para ascensor ID={ascensor_id}.'
    )

    return resultados


def serializar_diagnostico(resultados):
    """
    Convierte la lista de resultados del motor a formato JSON para
    almacenarla en el campo 'diagnostico_generado' del modelo Intervencion.

    Guardar el JSON en la base de datos permite regenerar el parte de trabajo
    PDF en cualquier momento sin volver a ejecutar el motor de inferencia,
    incluso si las reglas han cambiado desde que se realizó la intervención.

    Parámetros:
        resultados (list[dict]):
            Lista devuelta por obtener_diagnostico().

    Retorna:
        str: Cadena de texto en formato JSON.
    """
    # ensure_ascii=False permite que los caracteres españoles (á, é, ñ, etc.)
    # se guarden tal cual en lugar de como secuencias de escape (\u00e1, etc.).
    # indent=2 formatea el JSON con sangría para que sea legible si se inspecciona
    # directamente en la base de datos durante el desarrollo.
    return json.dumps(resultados, ensure_ascii=False, indent=2)


def deserializar_diagnostico(diagnostico_json):
    """
    Convierte el JSON almacenado en la base de datos de vuelta a la lista
    de diccionarios que usan las plantillas HTML y el generador de PDF.

    Parámetros:
        diagnostico_json (str):
            Cadena JSON almacenada en el campo Intervencion.diagnostico_generado.

    Retorna:
        list[dict]: Lista de causas probables, o lista vacía si el JSON
        está vacío o es inválido.
    """
    # Si el campo está vacío (intervención recién creada o sin diagnóstico),
    # devolvemos lista vacía para no provocar errores en las plantillas.
    if not diagnostico_json:
        return []

    try:
        return json.loads(diagnostico_json)
    except json.JSONDecodeError:
        # Si el JSON está malformado por algún motivo inesperado,
        # registramos el error y devolvemos lista vacía para que
        # la aplicación no se rompa.
        logger.error(
            f'Error al deserializar diagnóstico JSON: '
            f'{diagnostico_json[:100]}...'
        )
        return []