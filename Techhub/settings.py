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
]

# =======================================
# APPS
# =======================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'application',

    'cloudinary_storage',  # MUST be before django.contrib.staticfiles
    'cloudinary',
]

# =======================================
# MIDDLEWARE
# =======================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise in all environments
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
                'django.template.context_processors.media',  # Add this
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
    # Parse the URL manually to configure cloudinary
    import re
    match = re.match(r'cloudinary://(\d+):([^@]+)@([^/]+)', CLOUDINARY_URL)
    if match:
        cloudinary.config(
            cloud_name=match.group(3),
            api_key=match.group(1),
            api_secret=match.group(2),
            secure=True
        )

# =======================================
# STATIC FILES
# =======================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =======================================
# MEDIA FILES
# =======================================
if not DEBUG and CLOUDINARY_URL:
    # Production: Use Cloudinary
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    MEDIA_URL = '/media/'  # Cloudinary will handle this
else:
    # Development: Use local storage
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# =======================================
# LOGIN
# =======================================
LOGIN_URL = "login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"