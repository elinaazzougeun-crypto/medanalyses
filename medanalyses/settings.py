from pathlib import Path
from django.contrib.messages import constants as messages_constants
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────
# 🔐 SÉCURITÉ
# ─────────────────────────────────────────

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-bd-4e&)=gu9him&5_=kfat&fuq2jhsafi)($68xp)+cyy'  # dev seulement
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# ─────────────────────────────────────────
# 📦 APPLICATIONS
# ─────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps locales
    'analyses',
]


# ─────────────────────────────────────────
# ⚙️ MIDDLEWARE
# ─────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ─────────────────────────────────────────
# 🌐 URLS & WSGI
# ─────────────────────────────────────────

ROOT_URLCONF = 'medanalyses.urls'
WSGI_APPLICATION = 'medanalyses.wsgi.application'


# ─────────────────────────────────────────
# 🎨 TEMPLATES
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# 🗄️ BASE DE DONNÉES
# ─────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'medanalyses',
        'USER': 'postgres',
        'PASSWORD': 'ton_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# ─────────────────────────────────────────
# 🔑 VALIDATION MOTS DE PASSE
# ─────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─────────────────────────────────────────
# 🌍 INTERNATIONALISATION
# ─────────────────────────────────────────

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Algiers'
USE_I18N      = True
USE_TZ        = True


# ─────────────────────────────────────────
# 🗂️ FICHIERS STATIQUES & MÉDIA
# ─────────────────────────────────────────

STATIC_URL  = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # pour "collectstatic" en production

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'         # pour les fichiers uploadés


# ─────────────────────────────────────────
# 🔐 AUTHENTIFICATION
# ─────────────────────────────────────────

LOGIN_URL             = '/login/'
LOGIN_REDIRECT_URL    = '/dashboard/'
LOGOUT_REDIRECT_URL   = '/login/'

# Durée de session : 8 heures
SESSION_COOKIE_AGE    = 8 * 60 * 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# ─────────────────────────────────────────
# 💬 MESSAGES (notifications)
# ─────────────────────────────────────────

MESSAGE_TAGS = {
    messages_constants.DEBUG:   'secondary',
    messages_constants.INFO:    'info',
    messages_constants.SUCCESS: 'success',
    messages_constants.WARNING: 'warning',
    messages_constants.ERROR:   'danger',
}


# ─────────────────────────────────────────
# 🆔 CLÉ PRIMAIRE PAR DÉFAUT
# ─────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
