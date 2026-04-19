"""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología 
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

congif/settings.py ─ Configuración principal del proyecto Django.
Ref: https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


###  SEGURIDAD
# Configuración válida solo para desarrollo del TFG; no apta para producción.
SECRET_KEY = 'django-insecure-tfg-ascensores-cambia-esto-en-produccion'

DEBUG = True # Cambiar a False antes de un despliegue en real

ALLOWED_HOSTS = ['*'] # En producción restringir a un dominio concreto


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

        'DIRS': [BASE_DIR / 'templates'], # plantillas compartidas entre apps

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',   # Necesario para el admin
                'django.contrib.auth.context_processors.auth',  # Variable {{ user }}
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# BASE DE DATOS
# Se utiliza SQLite debido a que no requiere la instalación de ningún servidor adicional.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  
        'NAME': BASE_DIR / 'db.sqlite3',         
    }
}


# VALIDADOR DE CONTRASEÑAS
# Reglas para la creación de la contraseña
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# URL'S de AUTENTICACION
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/ascensores/'
LOGOUT_REDIRECT_URL = '/login/'


# INTERNACIONALIZACION
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
# Sin esto las fechas en el admin aparecen en UTC
USE_TZ = True


# FICHEROS ESTATICOS (CSS, JavaScript, imágenes) 
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

