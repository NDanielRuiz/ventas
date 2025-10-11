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
    # Mis Aplicaciones
    'ventas',
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

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==============================================================================
# CONFIGURACIONES ADICIONALES
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'