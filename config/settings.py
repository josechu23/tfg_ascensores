"""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

config/settings.py ─ Configuración principal del proyecto Django.
Ref: https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


### SEGURIDAD
# SECRET_KEY se lee desde variable de entorno en producción.
# El valor por defecto solo se usa en desarrollo local.
SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-local-para-desarrollo-no-usar-en-produccion')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost 127.0.0.1').split(' ')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'diagnostico',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# PLANTILLAS
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# BASE DE DATOS
# En producción (Render), DB_PATH apunta al disco persistente (/var/data/db.sqlite3).
# En desarrollo local, se usa db.sqlite3 en la raíz del proyecto.
_db_path = os.environ.get('DB_PATH', '')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(_db_path) if _db_path else BASE_DIR / 'db.sqlite3',
    }
}

# VALIDADOR DE CONTRASEÑAS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# URL'S DE AUTENTICACIÓN
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/ascensores/'
LOGOUT_REDIRECT_URL = '/login/'

# INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# FICHEROS ESTÁTICOS (CSS, JavaScript, imágenes)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'