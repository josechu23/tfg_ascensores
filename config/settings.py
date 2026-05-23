"""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología 
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

settings.py
───────────
Fichero de configuración principal del proyecto Django.
En este fichero se centralizan las decisiones técnicas del proyecto: seguridad, aplicaciones instaladas,
base de datos, autenticación, internacionalización y gestión de recursos estáticos

Documentación oficial: https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# BASE_DIR apunta a la carpeta raíz del proyecto (tfg_ascensores/).
# Path(__file__) es la ruta de este fichero (config/settings.py).
# .resolve() la convierte en ruta absoluta.
# .parent.parent sube dos niveles: de config/ a tfg_ascensores/.
BASE_DIR = Path(__file__).resolve().parent.parent


# ── Seguridad ─────────────────────────────────────────────────────────────────

# Clave secreta del proyecto
# En esta entrega se mantiene una clave de desarrollo; en despliegue real debe obtenerse
# desde variables de entorno o un gestor de secretos, nunca dejarse expuesta en el repositorio.
SECRET_KEY = 'django-insecure-tfg-ascensores-cambia-esto-en-produccion'

# Modo depuración activado únicamente durante el desarrollo del TFG.
# Permite ver trazas y mensajes detallados para facilitar la validación funcional.
# En producción debe establecerse siempre a False.
DEBUG = True

# Hosts permitidos durante el desarrollo local.
# Se usa '*' para permitir cualquier host y porque permite simplificar la ejecución en entorno de pruebas.
# En un entorno real debería restringirse a dominios concretos.
ALLOWED_HOSTS = ['*']


# ── Aplicaciones instaladas ───────────────────────────────────────────────────

# Django necesita conocer qué aplicaciones forman el proyecto.
# Las primeras seis son las apps internas de Django.
# 'diagnostico' es la app que he creado para este TFG.
INSTALLED_APPS = [
    'django.contrib.admin',          # Panel de administración web
    'django.contrib.auth',           # Sistema de autenticación de usuarios
    'django.contrib.contenttypes',   # Framework de tipos de contenido
    'django.contrib.sessions',       # Gestión de sesiones de usuario
    'django.contrib.messages',       # Sistema de mensajes flash
    'django.contrib.staticfiles',    # Gestión de ficheros estáticos (CSS, JS)
    'diagnostico',                   # Aplicación principal del sistema experto
]

# ── Middleware ────────────────────────────────────────────────────────────────

# El middleware son las capas de procesamiento que se aplican a cada una de las peticiones HTTP antes de llegar a la vista
#  y a cada respuesta antes de salir hacia el navegador. Se ejecutan en este orden definido aquí
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Cabeceras de seguridad HTTP
    'django.contrib.sessions.middleware.SessionMiddleware',    # Activa el sistema de sesiones
    'django.middleware.common.CommonMiddleware',               # Normalización de URLs
    'django.middleware.csrf.CsrfViewMiddleware',               # Protección contra CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Asocia usuario a la petición
    'django.contrib.messages.middleware.MessageMiddleware',    # Activa mensajes flash
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Protección contra clickjacking
]

# Indica a Django cuál es el fichero principal de configuración de URLs.
ROOT_URLCONF = 'config.urls'


# ── Plantillas HTML ───────────────────────────────────────────────────────────

TEMPLATES = [
    {
        # Motor de plantillas: el nativo de Django
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Carpetas donde Django buscará plantillas a nivel de proyecto.
        # BASE_DIR / 'templates' equivale a tfg_ascensores/templates/
        'DIRS': [BASE_DIR / 'templates'],

        # APP_DIRS = True. Esto indica que Django también buscará plantillas dentro de la carpeta templates/ de cada app instalada.
        'APP_DIRS': True,

        'OPTIONS': {
            # Procesadores de contexto: funciones que añaden variables automáticamente a todas las plantillas (usuario, mensajes, etc.)
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',   # Necesario para el admin
                'django.contrib.auth.context_processors.auth',  # Variable {{ user }}
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Módulo WSGI: punto de entrada para servidores web en producción.
WSGI_APPLICATION = 'config.wsgi.application'


# ── Base de datos ─────────────────────────────────────────────────────────────

# Configuración de la base de datos.
# Se utiliza SQLite debido a que no requiere la instalación de ningún servidor adicional.
# Django crea el fichero db.sqlite3 automáticamente al ejecutar las migraciones.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Motor de base de datos
        'NAME': BASE_DIR / 'db.sqlite3',          # Ruta del fichero de base de datos
    }
}


# ── Validadores de contraseña ─────────────────────────────────────────────────

# Django aplica las siguientes reglas al crear o cambiar contraseñas de usuario.
AUTH_PASSWORD_VALIDATORS = [
    # La contraseña no puede ser demasiado similar al nombre de usuario
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    # La contraseña debe tener al menos 8 caracteres
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    # La contraseña no puede ser una contraseña común (password, 123456, etc.)
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # La contraseña no puede ser completamente numérica
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ── URLs de autenticación ─────────────────────────────────────────────────────

# URL a la que Django redirige al usuario cuando intenta acceder a una página protegida sin estar autenticado.
LOGIN_URL = '/login/'

# URL a la que Django redirige al usuario tras iniciar sesión correctamente.
LOGIN_REDIRECT_URL = '/ascensores/'

# URL a la que Django redirige al usuario tras cerrar sesión.
LOGOUT_REDIRECT_URL = '/login/'


# ── Internacionalización ──────────────────────────────────────────────────────

# Idioma por defecto del panel de administración y mensajes de Django.
LANGUAGE_CODE = 'es-es'

# Zona horaria para el almacenamiento y visualización de fechas y horas.
TIME_ZONE = 'Europe/Madrid'

# USE_I18N = True activa el sistema de traducción de Django.
USE_I18N = True

# USE_TZ = True almacena las fechas en UTC en la base de datos y las convierte a TIME_ZONE al mostrarlas
USE_TZ = True


# ── Ficheros estáticos (CSS, JavaScript, imágenes) ────────────────────────────

# URL base desde la que el navegador solicitará los ficheros estáticos.
STATIC_URL = '/static/'

# Carpetas adicionales donde Django buscará ficheros estáticos además de la carpeta static/ de cada app.
STATICFILES_DIRS = [BASE_DIR / 'static']


# ── Clave primaria por defecto ────────────────────────────────────────────────

# Tipo de campo que Django usará como clave primaria en los modelos que no definan una explícitamente. 
# BigAutoField es un entero de 64 bits con autoincremento, suficiente para cualquier volumen de datos.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

