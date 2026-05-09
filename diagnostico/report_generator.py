import io
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def generar_parte_trabajo(intervencion):
    from .inference_engine import deserializar_diagnostico
    resultados = deserializar_diagnostico(intervencion.diagnostico_generado)

    html = render_to_string('diagnostico/parte_trabajo.html', {
        'intervencion': intervencion,
        'ascensor':     intervencion.ascensor,
        'tecnico':      intervencion.tecnico,
        'resultados':   resultados,
    })

    buffer = io.BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    buffer.seek(0)
    return buffer.read()
