import base64
import logging
import os
import socket
import sys

import grpc
from gqlauth.settings_type import GqlAuthSettings
from gqlauth.settings_type import id_field
from pathlib import Path
from standardwebhooks.webhooks import Webhook

from . import to_boolean
from . import create_token_type


DEBUG = to_boolean(os.getenv("DEBUG", False))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

BASE_DIR = Path(__file__).resolve().parent.parent

# https://randomkeygen.com/#504_wpa
SECRET_KEY = os.getenv("SECRET_KEY")

CSRF_TRUSTED_ORIGINS = ["https://*.ngrok-free.app"]

ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS = [
    "django_createsuperuser",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django_extensions",
    "behave_django",
    "core.apps.CoreConfig",
    "drf_spectacular",
    "gqlauth",
    "rest_framework_simplejwt",
    "rest_framework",
    "strawberry_django",
    "tracer",
]

MIDDLEWARE = [
    "tracer.middleware.RequestID",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "gqlauth.core.middlewares.django_jwt_middleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

MIGRATION_MODULES = {"core": "core.models.migrations"}

ROOT_URLCONF = "config.urls"

# https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-TEMPLATES
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            f"{BASE_DIR}/core/www/templates",
        ],
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

STATIC_URL = "static/"
STATIC_ROOT = f"{BASE_DIR}/core/www/static"

ASGI_APPLICATION = "config.asgi.application_django"
WSGI_APPLICATION = "config.wsgi.application_django"

# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    "postgres": {
        "development": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.getenv("POSTGRES_DB"),
            "USER": os.getenv("POSTGRES_USER"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            "HOST": os.getenv("POSTGRES_HOST"),
            "PORT": int(os.getenv("POSTGRES_PORT", 5432)),
            "TEST": {"NAME": "wfs_unittest"},
        }
    },
}

DATABASES["default"] = DATABASES["postgres"]

REDIS_ALERT_DB = 0
REDIS_CACHING_DB = 1
REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_PROTOCOL_SCHEMA = "redis"
REDIS_PROTOCOL_VERSION = 3

# See example configuration for a redis https://docs.djangoproject.com/en/5.1/topics/cache/#cache-arguments
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"{REDIS_PROTOCOL_SCHEMA}://{REDIS_HOST}:{REDIS_PORT}",
        "TIMEOUT": 300,
        "OPTIONS": {
            "db": REDIS_CACHING_DB
        }
    }
}
CACHE_TIMEOUT_SECONDS = 30

APPEND_SLASH = False

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# If USE_TZ is False then strawberry-django-auth will not work!
TIME_ZONE = "UTC"
USE_TZ = True

LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_L10N = True

# strawberry-django-auth
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# https://nrbnlulu.github.io/strawberry-django-auth/tutorial/#install-strawberry-django-auth
GQL_AUTH = GqlAuthSettings(
    LOGIN_REQUIRE_CAPTCHA=False,
    ALLOW_LOGIN_NOT_VERIFIED=False,
    JWT_PAYLOAD_HANDLER=create_token_type,
    JWT_PAYLOAD_PK=id_field,
    JWT_TIME_FORMAT="%s",
)

# Webhook
WEBHOOK_EXPIRATION_SECONDS = 3
WEBHOOK_PAYLOAD_MAX_SIZE_BYTES = 20 * 1024  # KiB
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
WEBHOOK_SECRET_B64 = base64.b64encode(WEBHOOK_SECRET.encode()).decode()

webhook = Webhook(WEBHOOK_SECRET_B64)

# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_APPEND_SLASH": False,
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 3,
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.QueryParameterVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ("v1", "v2"),
    "VERSION_PARAM": "version",
    "EXCEPTION_HANDLER": "core.helpers.handlers.exception_handler.request_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.AnonRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/minute"
    }
}

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "USER_ID_CLAIM": "id",
}

# https://strawberry.rocks/docs/django/guide/settings
STRAWBERRY_DJANGO = {
    "DEFAULT_PK_FIELD_NAME": "pk",
    "FIELD_DESCRIPTION_FROM_HELP_TEXT": True,
    "TYPE_DESCRIPTION_FROM_MODEL_DOCSTRING": True,
}

# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    "TITLE": "Weather Forecast Service API",
    "DESCRIPTION": "Weather Forecast Service",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# https://docs.djangoproject.com/en/5.1/topics/logging/#id3
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "formatters": {
        "console": {
            "format": "{levelname} {asctime} {message}",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            "style": "{",
        },
        "json": {
            "()": "config.logs.JSONFormatter",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["stdout"],
            "level": "ERROR",
            "propagate": False,
        },
    }
}

logger = logging.getLogger("django")

# https://django-extensions.readthedocs.io/en/latest/graph_models.html#default-settings
GRAPH_MODELS = {
  "all_applications": True,
  "group_models": True,
}

TESTING = "test" in sys.argv
if DEBUG and not TESTING:
    IPs = socket.gethostbyname_ex(socket.gethostname())[2]
    container_ips = [IP[: IP.rfind(".")] + ".1" for IP in IPs]
    INTERNAL_IPS += container_ips
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append(
        "strawberry_django.middlewares.debug_toolbar.DebugToolbarMiddleware"
    )

# https://docs.djangoproject.com/en/5.1/ref/settings/#data-upload-max-memory-size
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024 # 20 MiB
