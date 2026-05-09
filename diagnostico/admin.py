from django.contrib import admin

from .models import Subsistema, Sintoma, Regla, Ascensor, PerfilUsuario, Intervencion

admin.site.site_header = 'Sistema Experto de Diagnóstico de Averías'
admin.site.site_title = 'Sistema Experto'
admin.site.index_title = 'Panel de administración'


@admin.register(Subsistema)
class SubsistemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Sintoma)
class SintomaAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'subsistema', 'activo')
    list_filter = ('subsistema', 'activo')
    search_fields = ('descripcion',)


@admin.register(Regla)
class ReglaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'subsistema', 'causa_probable', 'criticidad', 'peso_base', 'activa')
    list_filter = ('subsistema', 'criticidad', 'activa')
    search_fields = ('nombre', 'causa_probable')
    filter_horizontal = ('sintomas_requeridos',)


@admin.register(Ascensor)
class AscensorAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'direccion', 'fabricante', 'tipo_ascensor', 'activo')
    list_filter = ('tipo_ascensor', 'fabricante', 'activo')
    search_fields = ('identificador', 'direccion', 'fabricante')
    filter_horizontal = ('tecnicos',)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol')
    list_filter = ('rol',)


@admin.register(Intervencion)
class IntervencionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ascensor', 'tecnico', 'fecha_inicio', 'resultado')
    list_filter = ('resultado', 'ascensor')
    search_fields = ('ascensor__identificador', 'tecnico__username', 'causa_confirmada')
    readonly_fields = ('fecha_inicio', 'diagnostico_generado', 'sintomas_registrados')

