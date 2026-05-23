"""
models.py
─────────
Define las seis entidades del modelo de datos del sistema experto.
Cada clase Python que hereda de models.Model se convierte en una
tabla de la base de datos SQLite cuando se ejecutan las migraciones.

Entidades definidas:
    1. Subsistema       → agrupa síntomas y reglas por área del ascensor
    2. Sintoma          → síntoma observable seleccionable por el técnico
    3. Regla            → regla IF-THEN de la base de conocimiento
    4. Ascensor         → instalación del parque gestionado
    5. PerfilUsuario    → extiende el usuario de Django con el rol del técnico
    6. Intervencion     → registro de cada intervención correctiva realizada
"""

from django.db import models
from django.contrib.auth.models import User  # Modelo de usuario nativo de Django


# ── 1. Subsistema ─────────────────────────────────────────────────────────────
class Subsistema(models.Model):
    """
    Representa un área funcional del ascensor.
    Sirve para organizar los síntomas y las reglas de diagnóstico
    en grupos coherentes que el técnico puede identificar fácilmente.

    Ejemplos: Puertas, Cabina, Motor, Maniobra, Grupo hidráulico.
    """

    # Nombre del subsistema. unique=True impide duplicados.
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre'
    )

    # Descripción opcional del subsistema para el panel de administración.
    descripcion = models.TextField(
        blank=True,          # Permite dejarlo vacío en el formulario
        verbose_name='Descripción'
    )

    class Meta:
        # Nombre legible en el panel de administración (singular y plural)
        verbose_name        = 'Subsistema'
        verbose_name_plural = 'Subsistemas'
        # Ordena los subsistemas alfabéticamente por nombre
        ordering            = ['nombre']

    def __str__(self):
        """
        Representación en texto del objeto.
        Django usa este método para mostrar el objeto en el panel
        de administración y en los campos de selección de formularios.
        """
        return self.nombre


# ── 2. Síntoma ────────────────────────────────────────────────────────────────
class Sintoma(models.Model):
    """
    Representa un síntoma observable que el técnico puede seleccionar
    durante una intervención correctiva.

    Cada síntoma pertenece a un subsistema. El técnico seleccionará
    uno o más síntomas del formulario y el motor de inferencia
    usará esa selección para activar las reglas correspondientes.
    """

    # Relación con el subsistema al que pertenece este síntoma.
    # on_delete=CASCADE significa que si se borra el subsistema,
    # se borran también todos sus síntomas.
    # related_name='sintomas' permite acceder desde un subsistema
    # a todos sus síntomas con: subsistema.sintomas.all()
    subsistema = models.ForeignKey(
        Subsistema,
        on_delete=models.CASCADE,
        related_name='sintomas',
        verbose_name='Subsistema'
    )

    # Descripción del síntoma tal como la verá el técnico en la app.
    descripcion = models.CharField(
        max_length=255,
        verbose_name='Descripción del síntoma'
    )

    # Permite desactivar un síntoma sin borrarlo de la base de datos.
    # Si activo=False, el síntoma no aparece en el formulario del técnico.
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    class Meta:
        verbose_name        = 'Síntoma'
        verbose_name_plural = 'Síntomas'
        # Ordena por subsistema primero y luego por descripción
        ordering            = ['subsistema', 'descripcion']

    def __str__(self):
        return f'{self.subsistema} — {self.descripcion}'


# ── 3. Regla ──────────────────────────────────────────────────────────────────
class Regla(models.Model):
    """
    Representa una regla IF-THEN de la base de conocimiento del sistema experto.

    Estructura lógica:
        IF todos los síntomas de 'sintomas_requeridos' están presentes
        THEN sugiere 'causa_probable' con los 'pasos_comprobacion'

    El motor de inferencia recorre todas las reglas activas y activa
    aquellas cuyas condiciones (síntomas requeridos) quedan satisfechas
    por los síntomas seleccionados por el técnico.
    """

    # Opciones de criticidad del diagnóstico según la ITC AEM 1.
    # Cada tupla es (valor_en_BD, etiqueta_legible).
    CRITICIDAD_CHOICES = [
        ('critico',   'Crítico'),    # Riesgo inmediato para la seguridad
        ('urgente',   'Urgente'),    # Requiere intervención en el día
        ('diferible', 'Diferible'),  # Puede programarse sin urgencia
    ]

    # Nombre descriptivo de la regla para identificarla en el panel de admin.
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre de la regla'
    )

    # Subsistema al que pertenece esta regla.
    # Permite filtrar reglas por subsistema en el motor de inferencia.
    subsistema = models.ForeignKey(
        Subsistema,
        on_delete=models.CASCADE,
        related_name='reglas',
        verbose_name='Subsistema'
    )

    # Relación muchos a muchos con Síntoma.
    # Una regla puede requerir varios síntomas,
    # y un síntoma puede aparecer en varias reglas.
    # Django crea automáticamente una tabla intermedia en la BD.
    sintomas_requeridos = models.ManyToManyField(
        Sintoma,
        related_name='reglas',
        verbose_name='Síntomas requeridos',
        help_text='La regla se activa cuando TODOS estos síntomas están presentes.'
    )

    # Causa probable que el motor sugiere al técnico cuando esta regla se activa.
    causa_probable = models.CharField(
        max_length=255,
        verbose_name='Causa probable'
    )

    # Pasos de comprobación recomendados para verificar esta causa.
    # Se almacenan como texto plano, un paso por línea.
    # La vista los divide por '\n' para mostrarlos como lista numerada.
    pasos_comprobacion = models.TextField(
        verbose_name='Pasos de comprobación',
        help_text='Un paso por línea. Se mostrarán como lista numerada al técnico.'
    )

    # Nivel de criticidad de esta causa según la ITC AEM 1.
    criticidad = models.CharField(
        max_length=10,
        choices=CRITICIDAD_CHOICES,
        default='urgente',
        verbose_name='Criticidad'
    )

    # Peso de probabilidad base de esta causa.
    # El motor de inferencia usa este valor para ordenar las causas.
    # Se puede incrementar dinámicamente en función del historial del ascensor.
    # Rango recomendado: 0.1 (muy improbable) a 10.0 (muy probable).
    peso_base = models.FloatField(
        default=1.0,
        verbose_name='Peso base',
        help_text='Probabilidad base de esta causa (0.1 – 10.0).'
    )

    # Permite desactivar una regla sin borrarla.
    # Las reglas inactivas no son procesadas por el motor de inferencia.
    activa = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )

    class Meta:
        verbose_name        = 'Regla de diagnóstico'
        verbose_name_plural = 'Reglas de diagnóstico'
        ordering            = ['subsistema', 'nombre']

    def __str__(self):
        # get_criticidad_display() devuelve la etiqueta legible del choice.
        return f'{self.nombre} [{self.get_criticidad_display()}]'


# ── 4. Ascensor ───────────────────────────────────────────────────────────────
class Ascensor(models.Model):
    """
    Representa una instalación del parque gestionado por la empresa mantenedora.
    El técnico selecciona el ascensor al iniciar una intervención correctiva (UC01).
    """

    # Tipos de ascensor reconocidos por la ITC AEM 1.
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

    # Dirección completa de la instalación.
    direccion = models.CharField(
        max_length=255,
        verbose_name='Dirección'
    )

    # Fabricante del ascensor (Otis, KONE, Schindler, Orona, etc.)
    fabricante = models.CharField(
        max_length=100,
        verbose_name='Fabricante'
    )

    # Modelo comercial del ascensor. Opcional.
    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Modelo'
    )

    # Tipo de maniobra instalada (p.ej. "Fermator VVVF", "Selcom ECO").
    # Campo libre porque la variedad de maniobras multimarca es muy grande.
    tipo_maniobra = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tipo de maniobra'
    )

    # Tipo de ascensor según la clasificación de la ITC AEM 1.
    tipo_ascensor = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        default='electrico_traccion',
        verbose_name='Tipo de ascensor'
    )

    # Año de instalación. null=True y blank=True permiten dejarlo vacío.
    anio_instalacion = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Año de instalación'
    )

    # Técnicos de campo asignados a esta instalación.
    # Relación muchos a muchos: un técnico puede tener varios ascensores
    # y un ascensor puede tener varios técnicos asignados.
    # blank=True permite ascensores sin técnico asignado aún.
    tecnicos = models.ManyToManyField(
        User,
        related_name='ascensores',
        blank=True,
        verbose_name='Técnicos asignados'
    )

    # Permite dar de baja un ascensor sin borrarlo de la base de datos,
    # conservando así su historial de intervenciones.
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


# ── 5. Perfil de usuario ──────────────────────────────────────────────────────
class PerfilUsuario(models.Model):
    """
    Extiende el modelo de usuario nativo de Django añadiendo el rol del técnico.

    Django ya gestiona nombre, contraseña y email en su propio modelo User.
    Este modelo añade únicamente el rol, que determina qué puede hacer
    cada usuario en la aplicación (control de acceso).

    La relación OneToOneField garantiza que cada usuario tiene exactamente
    un perfil y cada perfil pertenece exactamente a un usuario.
    """

    ROL_CHOICES = [
        ('tecnico_campo',  'Técnico de Campo'),   # Acceso al flujo de diagnóstico
        ('tecnico_senior', 'Técnico Sénior'),      # Además puede gestionar reglas
        ('administrador',  'Administrador'),        # Acceso total al sistema
    ]

    # Relación uno a uno con el modelo User de Django.
    # on_delete=CASCADE: si se borra el usuario, se borra también su perfil.
    # related_name='perfil' permite acceder al perfil desde un usuario con:
    # usuario.perfil.rol
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )

    # Rol del usuario en el sistema. Controla los permisos de acceso.
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
        # get_full_name() devuelve nombre y apellidos del usuario de Django.
        # get_rol_display() devuelve la etiqueta legible del choice.
        return f'{self.usuario.get_full_name()} ({self.get_rol_display()})'

    def es_tecnico_senior(self):
        """
        Devuelve True si el usuario puede gestionar la base de conocimiento.
        Tanto el Técnico Sénior como el Administrador tienen este permiso.
        Se usa en las vistas para controlar el acceso a UC07.
        """
        return self.rol in ('tecnico_senior', 'administrador')

    def es_administrador(self):
        """
        Devuelve True si el usuario tiene acceso total al sistema.
        Se usa en las vistas para controlar el acceso a UC08 y UC09.
        """
        return self.rol == 'administrador'


# ── 6. Intervención ───────────────────────────────────────────────────────────
class Intervencion(models.Model):
    """
    Registra cada intervención correctiva realizada sobre un ascensor.

    Este modelo es el eje central de la trazabilidad documental del sistema.
    Almacena todos los datos exigidos por el Real Decreto 355/2024 (ITC AEM 1)
    para las intervenciones de mantenimiento correctivo:
        - Ascensor intervenido
        - Técnico actuante
        - Fecha y hora de inicio y fin
        - Síntomas registrados
        - Diagnóstico generado por el motor de inferencia
        - Causa confirmada por el técnico
        - Acción correctiva aplicada
        - Resultado de la intervención

    Cada intervención puede generar un parte de trabajo en PDF (UC06).
    """

    RESULTADO_CHOICES = [
        ('resuelto',         'Resuelto'),
        ('no_resuelto',      'No resuelto'),
        ('derivado_senior',  'Derivado a Técnico Sénior'),
        ('no_diagnosticado', 'Causa no determinada'),
    ]

    # Ascensor sobre el que se realiza la intervención.
    # on_delete=PROTECT impide borrar un ascensor que tenga intervenciones,
    # protegiendo así el historial de trazabilidad.
    ascensor = models.ForeignKey(
        Ascensor,
        on_delete=models.PROTECT,
        related_name='intervenciones',
        verbose_name='Ascensor'
    )

    # Técnico que realiza la intervención.
    # on_delete=PROTECT por el mismo motivo que en ascensor.
    tecnico = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='intervenciones',
        verbose_name='Técnico'
    )

    # Fecha y hora de inicio. auto_now_add=True la establece automáticamente
    # al crear el registro, sin necesidad de que el técnico la introduzca.
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora de inicio'
    )

    # Fecha y hora de fin. null=True y blank=True porque se rellena
    # cuando el técnico confirma el fin de la intervención, no al crearla.
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha y hora de fin'
    )

    # Síntomas que el técnico seleccionó durante la intervención (RF02).
    # blank=True porque al crear la intervención aún no se han seleccionado.
    sintomas_registrados = models.ManyToManyField(
        Sintoma,
        related_name='intervenciones',
        blank=True,
        verbose_name='Síntomas registrados'
    )

    # Resultado del motor de inferencia almacenado como texto JSON.
    # Se guarda en crudo para poder regenerar el parte de trabajo
    # en cualquier momento sin volver a ejecutar el motor.
    # Ejemplo: '[{"causa": "Operador defectuoso", "peso": 2.5, ...}]'
    diagnostico_generado = models.TextField(
        blank=True,
        verbose_name='Diagnóstico generado',
        help_text='JSON con la lista de causas probables devuelta por el motor.'
    )

    # Causa que el técnico ha confirmado tras realizar las comprobaciones.
    # Puede diferir de la primera causa sugerida por el motor.
    causa_confirmada = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Causa confirmada'
    )

    # Descripción de la acción correctiva que el técnico ha aplicado.
    accion_correctiva = models.TextField(
        blank=True,
        verbose_name='Acción correctiva aplicada'
    )

    # Observaciones adicionales del técnico (campo libre).
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )

    # Resultado final de la intervención.
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        default='resuelto',
        verbose_name='Resultado'
    )

    class Meta:
        verbose_name        = 'Intervención'
        verbose_name_plural = 'Intervenciones'
        # Las intervenciones más recientes aparecen primero en el listado.
        ordering            = ['-fecha_inicio']

    def __str__(self):
        return (
            f'Intervención #{self.pk} — '
            f'{self.ascensor.identificador} — '
            f'{self.fecha_inicio.strftime("%d/%m/%Y %H:%M")}'
        )