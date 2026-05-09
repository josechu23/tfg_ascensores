"""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

report_generator.py ─ Generación del parte de trabajo en PDF.
Utiliza xhtml2pdf para convertir una plantilla HTML de Django a PDF,
sin dependencias de librerías del sistema operativo.
"""

import io
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def generar_parte_trabajo(intervencion):
    """
    Recibe un objeto Intervencion y devuelve los bytes del PDF generado.
    La estructura del documento se define en la plantilla HTML correspondiente.
    """

    # Deserializar el diagnóstico para pasarlo a la plantilla
    from .inference_engine import deserializar_diagnostico
    resultados = deserializar_diagnostico(intervencion.diagnostico_generado)

    # Renderizar la plantilla HTML con los datos de la intervención
    html = render_to_string(
        'diagnostico/parte_trabajo.html',
        {
            'intervencion': intervencion,
            'ascensor':     intervencion.ascensor,
            'tecnico':      intervencion.tecnico,
            'resultados':   resultados,
        }
    )

    # Convertir el HTML a PDF en memoria
    buffer = io.BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    buffer.seek(0)
    return buffer.read()