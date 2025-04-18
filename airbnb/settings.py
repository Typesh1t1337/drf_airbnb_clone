"""
Django settings for airbnb project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
from datetime import timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-a@xwgesll+c5gk9y+)nta6cw5&01yn+z4dbauu6d4*7j&-n1bm"

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "192.168.0.106", "0.0.0.0"]


# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "storages",
    "app.apps.AppConfig",
    "account.apps.AccountConfig",
    "django_celery_beat",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "airbnb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates']
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "airbnb.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "airbnb_postgres",
        "USER": "postgres",
        "PASSWORD": "root",
        "PORT": "5432",
        "HOST": "airbnb_postgres",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]



LANGUAGE_CODE = "ru"

TIME_ZONE = "Asia/Almaty"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

REST_USE_JWT = True

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "AUTH_COOKIE_SECURE": False,
    'TOKEN_COOKIE_HTTP_ONLY': True,
    "AUTH_COOKIE_SAMESITE": "Lax",
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "account.dependencies.CustomJWTAuth",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    )
}

CELERY_IMPORTS = ("app.tasks", "account.tasks")
CELERY_BROKER_URL = "amqp://airbnb:root@broker:5672/"
CELERY_RESULT_BACKEND = "rpc://"
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTH_USER_MODEL = "account.User"


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://airbnb_redis:6379/0",
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://192.168.0.106:5173",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_METHODS = ["GET", "POST", "DELETE", "OPTIONS"]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "offerkz.codesender@gmail.com"
EMAIL_HOST_PASSWORD = "unra xahx pnzv jgrx"

AWS_S3_ENDPOINT_URL = "http://172.22.0.3:9000"
AWS_STORAGE_BUCKET_NAME = "housing"
AWS_QUERYSTRING_AUTH = False
AWS_S3_BUCKET_AUTH = False
AWS_S3_USE_HTTPS = False
AWS_ACCESS_KEY_ID = "airbnb"
AWS_SECRET_ACCESS_KEY = "airbnb_123"
AWS_S3_ADDRESSING_STYLE = "path"
AWS_FILE_OVERWRITE = False
AWS_S3_SECURE_URLS = False


DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"