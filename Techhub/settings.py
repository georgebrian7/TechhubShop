"""
Django settings for Techhub project.
"""

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
from decouple import config
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =======================================
# SECURITY
# =======================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "techhubpage.onrender.com",
    "www.keshilimited.com",
    "keshilimited.com",
    "*"
]

# =======================================
# APPS - ORDER IS CRITICAL
# =======================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # Add this for development
    'django.contrib.staticfiles',

    'application',
    'mpesa',
    'cloudinary_storage',
    'cloudinary',
]

# =======================================
# MIDDLEWARE
# =======================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Techhub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # Important for media files
                'django.template.context_processors.static',  # Important for static files
            ],
        },
    },
]

WSGI_APPLICATION = 'Techhub.wsgi.application'

# =======================================
# DATABASE
# =======================================
DATABASES = {
    "default": dj_database_url.config(
        default="postgresql://postgres:fancyMe@127.0.0.1:5432/postgres",
        conn_max_age=600
    )
}

# =======================================
# PASSWORDS
# =======================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =======================================
# INTERNATIONALIZATION
# =======================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =======================================
# CLOUDINARY CONFIGURATION
# =======================================
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL")

if CLOUDINARY_URL:
    import re
    match = re.match(r'cloudinary://(\d+):([^@]+)@([^/]+)', CLOUDINARY_URL)
    if match:
        cloudinary.config(
            cloud_name=match.group(3),
            api_key=match.group(1),
            api_secret=match.group(2),
            secure=True
        )
        print(f"✓ Cloudinary configured: {match.group(3)}")
    else:
        print("✗ Invalid CLOUDINARY_URL format")
else:
    print("⚠ CLOUDINARY_URL not set - using local storage")

# =======================================
# STATIC FILES
# =======================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# Only use STATICFILES_DIRS in development or if you have a separate static folder
if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / "static"]

# Use Whitenoise for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =======================================
# MEDIA FILES
# =======================================
if CLOUDINARY_URL and not DEBUG:
    # Production: Use Cloudinary
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    MEDIA_URL = '/media/'
    print("✓ Using Cloudinary for media storage")
else:
    # Development: Use local storage
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
    print("✓ Using local media storage")

# =======================================
# LOGIN
# =======================================
LOGIN_URL = "login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =======================================
# LOGGING (helpful for debugging)
# =======================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

CSRF_TRUSTED_ORIGINS = [
    "https://keshilimited.com",
    "https://www.keshilimited.com",
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



# Looking to send emails in production? Check out our Email API/SMTP product!


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='sandbox.smtp.mailtrap.io')
EMAIL_PORT = config('EMAIL_PORT', default=2525, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='TechHub <noreply@techhub.com>')


# EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
# EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='TechHub <noreply@techhub.com>')