import os

from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'unsafe-secret-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "whitenoise.runserver_nostatic",
    'corsheaders',
    'catalog',
    'order',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'contrib.context.middleware.ContextMiddleware',
]

ROOT_URLCONF = 'romashka.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            Path(BASE_DIR, "templates"),
            Path(BASE_DIR, "contrib", "openapi", "swagger_ui", "templates"),
            Path(BASE_DIR, "contrib", "openapi", "redoc_ui", "templates"),
        ],
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

WSGI_APPLICATION = 'romashka.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'mydb'),
        'USER': os.environ.get('POSTGRES_USER', 'myuser'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'mypassword'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_GETTEXT_SERVICE = "django.utils.translation.gettext"
LOCALE_LAZY_GETTEXT_SERVICE = "django.utils.translation.gettext_lazy"

DEFAULT_PYDANTIC_REQUEST_MODEL_MIXIN = "contrib.pydantic.mixins.django.model.DjangoRequestModelMixin"
DEFAULT_PYDANTIC_RESPONSE_MODEL_MIXIN = "contrib.pydantic.mixins.django.model.DjangoResponseModelMixin"
DEFAULT_PYDANTIC_PROXY_MODEL_MIXIN = "contrib.pydantic.mixins.django.model.DjangoProxyModelMixin"

EXTERNAL_CODE_MODEL = None

PRINT_API_EXCEPTIONS = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_DIRS = [
    # Path(BASE_DIR, "templates"),
    Path(BASE_DIR, "contrib", "openapi", "swagger_ui", "static"),
    Path(BASE_DIR, "contrib", "openapi", "redoc_ui", "static"),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # для Vite/Vue
    "http://localhost:3000",  # для React (если нужно)
    "http://192.168.1.115:5173"
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

PROJECT_URL = "http://192.168.1.115:8000"
