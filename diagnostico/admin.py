"""

Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología 
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

admin.py - Registra los modelos de la app diagnostico en el panel de administración

"""

from django.contrib import admin

admin.site.site_header = 'Sistema Experto de Diagnóstico de Averías'
admin.site.site_title = 'Sistema Experto'
admin.site.index_title = 'Panel de administración'

from .models import (
    Subsistema,
    Sintoma,
    Regla,
    Ascensor,
    PerfilUsuario,
    Intervencion,
)

# SUBSISTEMA
@admin.register(Subsistema)
class SubsistemaAdmin(admin.ModelAdmin):

    list_display = ('nombre', 'descripcion')

    search_fields = ('nombre',)


# SINTOMA
@admin.register(Sintoma)
class SintomaAdmin(admin.ModelAdmin):

    list_display = ('descripcion', 'subsistema', 'activo')

    list_filter = ('subsistema', 'activo')

    search_fields = ('descripcion',)


# REGLA
@admin.register(Regla)
class ReglaAdmin(admin.ModelAdmin):
    """
    En este módulo el Técnico Sénior gestiona la base de conocimiento (UC07).
    """

    list_display = (
        'nombre',
        'subsistema',
        'causa_probable',
        'criticidad',
        'peso_base',
        'activa'
    )

    list_filter = ('subsistema', 'criticidad', 'activa')

    search_fields = ('nombre', 'causa_probable')

    filter_horizontal = ('sintomas_requeridos',)


# ASCENSOR
@admin.register(Ascensor)
class AscensorAdmin(admin.ModelAdmin):

    list_display = (
        'identificador',
        'direccion',
        'fabricante',
        'tipo_ascensor',
        'activo'
    )

    list_filter = ('tipo_ascensor', 'fabricante', 'activo')

    search_fields = ('identificador', 'direccion', 'fabricante')

    filter_horizontal = ('tecnicos',)


# PERFIL DE USUARIO
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):

    list_display = ('usuario', 'rol')

    list_filter = ('rol',)


# INTERVENCION
@admin.register(Intervencion)
class IntervencionAdmin(admin.ModelAdmin):

    list_display = ('pk', 'ascensor', 'tecnico', 'fecha_inicio', 'resultado')

    list_filter = ('resultado', 'ascensor')

    search_fields = (
        'ascensor__identificador',  # __ permite buscar en campos relacionados
        'tecnico__username',
        'causa_confirmada'
    )

    readonly_fields = ('fecha_inicio',)