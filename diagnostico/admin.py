"""
admin.py
────────
Registra los modelos de la app 'diagnostico' en el panel de administración
de Django (http://127.0.0.1:8000/admin).

Para cada modelo se define una clase Admin que personaliza cómo se muestra
y se gestiona ese modelo en el panel: qué columnas aparecen en el listado,
qué filtros laterales están disponibles, qué campos son buscables, etc.

El panel de administración es la herramienta principal para:
    - Que el Técnico Sénior gestione la base de conocimiento (UC07)
    - Que el Administrador gestione el parque de ascensores (UC08)
    - Que el Administrador gestione los usuarios del sistema (UC09)
"""

from django.contrib import admin
from .models import (
    Subsistema,
    Sintoma,
    Regla,
    Ascensor,
    PerfilUsuario,
    Intervencion,
)


# ── Subsistema ────────────────────────────────────────────────────────────────
@admin.register(Subsistema)
class SubsistemaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Subsistema.
    """

    # Columnas que aparecen en la tabla del listado de subsistemas.
    list_display = ('nombre', 'descripcion')

    # Campos en los que funciona el buscador del panel de admin.
    search_fields = ('nombre',)


# ── Síntoma ───────────────────────────────────────────────────────────────────
@admin.register(Sintoma)
class SintomaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Sintoma.
    """

    # Columnas visibles en el listado.
    list_display = ('descripcion', 'subsistema', 'activo')

    # Filtros laterales: permiten filtrar la lista por subsistema o por activo.
    list_filter = ('subsistema', 'activo')

    # Campos en los que funciona el buscador.
    search_fields = ('descripcion',)


# ── Regla ─────────────────────────────────────────────────────────────────────
@admin.register(Regla)
class ReglaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Regla.
    Es el modelo más importante del panel porque aquí el Técnico Sénior
    gestiona la base de conocimiento del sistema experto (UC07).
    """

    # Columnas visibles en el listado de reglas.
    list_display = (
        'nombre',
        'subsistema',
        'causa_probable',
        'criticidad',
        'peso_base',
        'activa'
    )

    # Filtros laterales por subsistema, criticidad y estado activo/inactivo.
    list_filter = ('subsistema', 'criticidad', 'activa')

    # Campos en los que funciona el buscador.
    search_fields = ('nombre', 'causa_probable')

    # filter_horizontal muestra el campo ManyToMany 'sintomas_requeridos'
    # como un widget de dos columnas (disponibles | seleccionados),
    # que es mucho más cómodo que una lista desplegable múltiple.
    filter_horizontal = ('sintomas_requeridos',)


# ── Ascensor ──────────────────────────────────────────────────────────────────
@admin.register(Ascensor)
class AscensorAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Ascensor.
    Permite al Administrador gestionar el parque de ascensores (UC08).
    """

    # Columnas visibles en el listado de ascensores.
    list_display = (
        'identificador',
        'direccion',
        'fabricante',
        'tipo_ascensor',
        'activo'
    )

    # Filtros laterales.
    list_filter = ('tipo_ascensor', 'fabricante', 'activo')

    # Campos buscables.
    search_fields = ('identificador', 'direccion', 'fabricante')

    # Widget de dos columnas para asignar técnicos al ascensor.
    filter_horizontal = ('tecnicos',)


# ── Perfil de usuario ─────────────────────────────────────────────────────────
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo PerfilUsuario.
    Permite al Administrador asignar roles a los usuarios (UC09).
    """

    # Muestra el usuario y su rol en el listado.
    list_display = ('usuario', 'rol')

    # Filtro lateral por rol.
    list_filter = ('rol',)


# ── Intervención ──────────────────────────────────────────────────────────────
@admin.register(Intervencion)
class IntervencionAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Intervencion.
    Permite consultar el historial de intervenciones correctivas.
    En condiciones normales el técnico no crea intervenciones desde el admin,
    sino desde la interfaz web de la app. El admin sirve solo para consulta.
    """

    # Columnas visibles en el listado de intervenciones.
    list_display = ('pk', 'ascensor', 'tecnico', 'fecha_inicio', 'resultado')

    # Filtros laterales.
    list_filter = ('resultado', 'ascensor')

    # Campos buscables: por identificador del ascensor, username del técnico
    # o causa confirmada.
    search_fields = (
        'ascensor__identificador',  # __ permite buscar en campos relacionados
        'tecnico__username',
        'causa_confirmada'
    )

    # readonly_fields impide modificar estos campos desde el admin.
    # fecha_inicio se establece automáticamente y no debe editarse manualmente.
    readonly_fields = ('fecha_inicio',)