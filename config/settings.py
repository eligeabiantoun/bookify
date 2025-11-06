from pathlib import Path
import environ
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# ---------------------------------------------------------------------
# BASE + ENV
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "restaurants",
    "accounts",
]

AUTH_USER_MODEL = "accounts.User"

# ---------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------------------------------------------------
# URLS / WSGI
# ---------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# ---------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------
# Use DATABASE_URL if provided (e.g., Postgres on Neon/Render); otherwise fall back to local SQLite
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# If your provider requires SSL (Neon usually does), either ensure
# ?sslmode=require is in the URL OR force it here:
if DATABASES["default"]["ENGINE"].endswith("postgresql") and "OPTIONS" not in DATABASES["default"]:
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

# ---------------------------------------------------------------------
# PASSWORD VALIDATORS
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# I18N / TZ
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Optional for deployments that run collectstatic:
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------------------------------------------------------------
# EMAIL (console backend for dev)
# ---------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@bookify.local"

# ---------------------------------------------------------------------
# AUTH BACKENDS
# ---------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "accounts.auth_backend.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ---------------------------------------------------------------------
# DEFAULT FIELD TYPE
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# AUTH FLOW (🔧 important for your bug fix)
# ---------------------------------------------------------------------
LOGIN_URL = "login"                       # your login url_name
LOGIN_REDIRECT_URL = "post_login" 
LOGOUT_REDIRECT_URL = "/"

# ---------------------------------------------------------------------
# DEV SECURITY HELPERS
# ---------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
