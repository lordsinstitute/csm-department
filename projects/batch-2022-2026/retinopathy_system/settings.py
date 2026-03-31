import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom Apps
    'users',
    'images',
    'detection',
    'tracking',
    'reports',
    'custom_admin',
    'dashboard',
   
    
    # Third Party
    'crispy_forms',
    'crispy_bootstrap5',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'retinopathy_system.urls'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='retinopathy_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default='root'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_REDIRECT_URL = 'dashboard:home'
LOGIN_URL = 'users:login'
LOGOUT_REDIRECT_URL = 'users:login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Non-fundus detection heuristic thresholds (tunable via .env)
NON_FUNDUS_STD_THRESHOLD = config('NON_FUNDUS_STD_THRESHOLD', default=12.0, cast=float)
NON_FUNDUS_MEAN_THRESHOLD = config('NON_FUNDUS_MEAN_THRESHOLD', default=30.0, cast=float)

# Additional non-fundus heuristic thresholds
NON_FUNDUS_RED_PROP = config('NON_FUNDUS_RED_PROP', default=0.015, cast=float)
NON_FUNDUS_RED_VS_GREEN = config('NON_FUNDUS_RED_VS_GREEN', default=10.0, cast=float)
