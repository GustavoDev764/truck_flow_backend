"""
Configurações base do Django.

Este módulo contém valores compartilhados entre os ambientes (dev/prod).
"""

from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
from config.env import env


def _parse_jwt_expires(expr: str) -> timedelta:
    """Converte '7d', '24h', '60m' em timedelta."""
    expr = (expr or "7d").strip().lower()
    if expr.endswith("d"):
        return timedelta(days=int(expr[:-1] or 7))
    if expr.endswith("h"):
        return timedelta(hours=int(expr[:-1] or 24))
    if expr.endswith("m"):
        return timedelta(minutes=int(expr[:-1] or 60))
    return timedelta(days=7)


SECRET_KEY = "django-insecure-%n%&j0*j-#ru2li8oahpax12j^kh#v$jv_jrs=5$-2(c65rcnn"


DEBUG = True

ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "core",
    "apps.accounts",
    "apps.trucks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DB_PROVIDER = env.DB_PROVIDER

if DB_PROVIDER in {"postgresql", "postgres"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env.DB_NAME,
            "USER": env.DB_USER,
            "PASSWORD": env.DB_PASSWORD,
            "HOST": env.DB_HOST,
            "PORT": env.DB_PORT,
        }
    }
else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.authentication.SessionAwareJWTAuthentication",
    ],
    "EXCEPTION_HANDLER": "config.exception_handler.api_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": _parse_jwt_expires(env.JWT_EXPIRES_IN),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}
if env.JWT_SECRET:
    SIMPLE_JWT["SIGNING_KEY"] = env.JWT_SECRET

SPECTACULAR_SETTINGS = {
    "TITLE": "TruckFlow API",
    "DESCRIPTION": "Documentacao das rotas TruckFlow",
    "VERSION": "1.0.0",
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOW_CREDENTIALS = False
