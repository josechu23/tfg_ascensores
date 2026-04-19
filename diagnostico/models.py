"""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología 
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

models.py - Se definen las seis entidades del modelo de datos del sistema experto.

Entidades definidas:
    1. Subsistema: agrupa síntomas y reglas por área del ascensor
    2. Sintoma: síntoma observable seleccionable por el técnico
    3. Regla: regla IF-THEN de la base de conocimiento
    4. Ascensor: instalación del parque gestionado
    5. PerfilUsuario: extiende el usuario con el rol del Técnico de Campo y Técnico Sénior
    6. Intervencion: registro de cada intervención correctiva realizada
"""

from django.db import models
from django.contrib.auth.models import User


# SUBSISTEMA
class Subsistema(models.Model):

    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre'
    )

    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )

    class Meta:
        verbose_name        = 'Subsistema'
        verbose_name_plural = 'Subsistemas'
        ordering            = ['nombre']

    def __str__(self):
        return self.nombre


# SINTOMA
class Sintoma(models.Model):
    # Síntoma observable vinculado a un subsistema. El técnico lo selecciona en RF02

    subsistema = models.ForeignKey(
        Subsistema,
        on_delete=models.CASCADE,
        related_name='sintomas',
        verbose_name='Subsistema'
    )

    descripcion = models.CharField(
        max_length=255,
        verbose_name='Descripción del síntoma'
    )

    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    class Meta:
        verbose_name        = 'Síntoma'
        verbose_name_plural = 'Síntomas'
        ordering            = ['subsistema', 'descripcion']

    def __str__(self):
        return f'{self.subsistema} — {self.descripcion}'


# REGLA
class Regla(models.Model):

    # Niveles según ITC AEM 1
    CRITICIDAD_CHOICES = [
        ('critico',   'Crítico'),  
        ('urgente',   'Urgente'),  
        ('diferible', 'Diferible'), 
    ]

    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre de la regla'
    )

    subsistema = models.ForeignKey(
        Subsistema,
        on_delete=models.CASCADE,
        related_name='reglas',
        verbose_name='Subsistema'
    )

    sintomas_requeridos = models.ManyToManyField(
        Sintoma,
        related_name='reglas',
        verbose_name='Síntomas requeridos',
        help_text='La regla se activa cuando TODOS estos síntomas están presentes.'
    )

    causa_probable = models.CharField(
        max_length=255,
        verbose_name='Causa probable'
    )

    pasos_comprobacion = models.TextField(
        verbose_name='Pasos de comprobación',
        help_text='Un paso por línea. Se mostrarán como lista numerada al técnico.'
    )

    criticidad = models.CharField(
        max_length=10,
        choices=CRITICIDAD_CHOICES,
        default='urgente',
        verbose_name='Criticidad'
    )

    # El motor utiliza este valor para ordenar las causas..
    peso_base = models.FloatField(
        default=1.0,
        verbose_name='Peso base',
        help_text='Probabilidad base de esta causa (0.1 – 10.0).'
    )

    activa = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )

    class Meta:
        verbose_name        = 'Regla de diagnóstico'
        verbose_name_plural = 'Reglas de diagnóstico'
        ordering            = ['subsistema', 'nombre']

    def __str__(self):
        return f'{self.nombre} [{self.get_criticidad_display()}]'


# ASCENSOR
class Ascensor(models.Model):
    """
    Instalación del parque de ascensores. El técnico la selecciona al iniciar UC01.
    """

    TIPO_CHOICES = [
        ('electrico_traccion',  'Eléctrico de tracción'),
        ('hidraulico',          'Hidráulico'),
        ('sin_cuarto_maquinas', 'Sin cuarto de máquinas (MRL)'),
        ('montacargas',         'Montacargas'),
        ('otro',                'Otro'),
    ]

    # Código interno o número de contrato. Debe ser único por instalación.
    identificador = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Identificador',
        help_text='Código interno o número de contrato.'
    )

    direccion = models.CharField(
        max_length=255,
        verbose_name='Dirección'
    )

    fabricante = models.CharField(
        max_length=100,
        verbose_name='Fabricante'
    )

    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Modelo'
    )

    # Campo libre. Gran variedad de maniobras.
    tipo_maniobra = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tipo de maniobra'
    )

    tipo_ascensor = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        default='electrico_traccion',
        verbose_name='Tipo de ascensor'
    )

    anio_instalacion = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Año de instalación'
    )

    tecnicos = models.ManyToManyField(
        User,
        related_name='ascensores',
        blank=True,
        verbose_name='Técnicos asignados'
    )

    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    class Meta:
        verbose_name        = 'Ascensor'
        verbose_name_plural = 'Ascensores'
        ordering            = ['direccion']

    def __str__(self):
        return f'{self.identificador} — {self.direccion}'


# PERFIL DE USUARIO
class PerfilUsuario(models.Model):

    ROL_CHOICES = [
        ('tecnico_campo',  'Técnico de Campo'),
        ('tecnico_senior', 'Técnico Sénior'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='tecnico_campo',
        verbose_name='Rol'
    )

    class Meta:
        verbose_name        = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'{self.usuario.get_full_name()} ({self.get_rol_display()})'

    def es_tecnico_senior(self):
        return self.rol == 'tecnico_senior'


# INTERVENCION
class Intervencion(models.Model):
    """
    Registro de cada intervención correctiva. Trazabilidad documental
    exigida por el RD 355/2024. Puede generar parte de trabajo en PDF (UC06).
    """

    RESULTADO_CHOICES = [
        ('resuelto',         'Resuelto'),
        ('no_resuelto',      'No resuelto'),
        ('derivado_senior',  'Derivado a Técnico Sénior'),
        ('no_diagnosticado', 'Causa no determinada'),
    ]

    # PROTECT para no perder el historial si se da de baja ascensor o técnico
    ascensor = models.ForeignKey(
        Ascensor,
        on_delete=models.PROTECT,
        related_name='intervenciones',
        verbose_name='Ascensor'
    )

    tecnico = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='intervenciones',
        verbose_name='Técnico'
    )

    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora de inicio'
    )

    # Se rellena cuando el técnico confirma el fin de la intervención.
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha y hora de fin'
    )

    sintomas_registrados = models.ManyToManyField(
        Sintoma,
        related_name='intervenciones',
        blank=True,
        verbose_name='Síntomas registrados'
    )

    diagnostico_generado = models.TextField(
        blank=True,
        verbose_name='Diagnóstico generado',
        help_text='JSON con la lista de causas probables devuelta por el motor.'
    )

    causa_confirmada = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Causa confirmada'
    )

    accion_correctiva = models.TextField(
        blank=True,
        verbose_name='Acción correctiva aplicada'
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )

    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        default='resuelto',
        verbose_name='Resultado'
    )

    class Meta:
        verbose_name        = 'Intervención'
        verbose_name_plural = 'Intervenciones'
        ordering            = ['-fecha_inicio']

    def __str__(self):
        return (
            f'Intervención #{self.pk} — '
            f'{self.ascensor.identificador} — '
            f'{self.fecha_inicio.strftime("%d/%m/%Y %H:%M")}'
        )