"""
Django settings for core_config project.
"""

from pathlib import Path
import os
import dj_database_url # Necesitamos importar esta librería

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD Y ENTORNO (PARA LOCAL Y PRODUCCIÓN)
# ==============================================================================

# La clave secreta se lee desde una variable de entorno en producción.
# Para desarrollo local, usamos una clave por defecto (no segura).
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-tu-clave-local-debe-ser-diferente')

# DEBUG se activa si la variable de entorno DEBUG es 'True'. Por defecto es False en producción.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Los hosts permitidos. Se añade el de Render automáticamente si existe.
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
else:
    # Para desarrollo local
    ALLOWED_HOSTS.append('127.0.0.1')


# ==============================================================================
# APLICACIONES Y MIDDLEWARE
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps de Terceros
    'storages',
    
    # Mis Aplicaciones
    'ventas',
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

ROOT_URLCONF = 'core_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'core_config.wsgi.application'


# ==============================================================================
# BASE DE DATOS (PARA LOCAL Y PRODUCCIÓN)
# ==============================================================================

DATABASES = {
    # Render nos dará una variable de entorno 'DATABASE_URL' que dj_database_url leerá.
    # Para desarrollo local, usará la URL que definimos aquí.
    'default': dj_database_url.config(
        default='postgresql://postgres:dbpass123@127.0.0.1:5432/gestordb',
        conn_max_age=600
    )
}


# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS E INTERNACIONALIZACIÓN
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# ARCHIVOS ESTÁTICOS Y MULTIMEDIA
# ==============================================================================

STATIC_URL = '/static/'
# Directorio donde Django buscará tus archivos estáticos (CSS, JS) en desarrollo.
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# Directorio donde `collectstatic` copiará todos los archivos estáticos para producción.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==============================================================================
# CONFIGURACIONES ADICIONALES
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'


# core_config/settings.py
# ... (al final del todo, después de LOGIN_REDIRECT_URL)

# ==============================================================================
# CONFIGURACIÓN DE ALMACENAMIENTO EN AWS S3 (SOLO PARA PRODUCCIÓN)
# ==============================================================================

if not DEBUG: # Solo se ejecuta cuando estamos en el servidor de Render (DEBUG=False)
    # Credenciales de AWS (leídas desde las variables de entorno de Render)
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    # Nombre del bucket de S3
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    # Región de AWS donde está tu bucket
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')

    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_FILE_OVERWRITE = False # No sobreescribir archivos con el mismo nombre

    AWS_DEFAULT_ACL = 'public-read'

    # Le decimos a Django que use S3Boto3Storage para los archivos multimedia
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # La URL base para los archivos multimedia ahora apuntará a S3
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"