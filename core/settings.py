"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-3_fdm44-wwn+h)al&$kc!sm0tydnoq^+&17k%99u+lm=a$ewfq"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "user",
    "restaurant",
    "rider",
    "landingapp",
    "modelapp",
    "paymentapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
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

WSGI_APPLICATION = "core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
#
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
#
#
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": 'FreshBiteDB',
#         "USER": 'root',
#         "PASSWORD": 'password',
#         "HOST": '127.0.0.1',
#         "PORT": '3306',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Karachi"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
AUTH_USER_MODEL = "modelapp.Person"


GOOGLE_MAPS_API_KEY = "AIzaSyBDTKCFj4lBwQoGrG4VbzaGIxQpCRXzOqs"
STRIPE_PUBLISHABLE_KEY = "pk_test_51PbgJKH3geCYyWafjYheOz2ZdT5Ng5teCa81DYGnW6wrphrHsewJ3FFXqbhovCjOSNCfzubKWBkmElSlNnxMBkiS00IPfIh9ye"
STRIPE_SECRET_KEY = "sk_test_51PbgJKH3geCYyWaf46ck61SvWZIaCmf0Trcl52yq04T7L4RZEJPr7QG7nwIT0gjHl4w6A5nuRy97UfSjk2dgNTUn006JOjdYAf"
ENDPOINT_SECRET = 'whsec_23fb92a362197d88adc4f06b9a43ecb92b8d4af49c367d75cf11a24c7b051e1c'

SERVER_DOMAIN = "http://127.0.0.1:8000/"

# SMTP_SERVER = 'smtp.mailersend.net'
# SMTP_PORT = 587
# SMTP_PASSWORD = 'MPqknV2VO7Zg7nBw'

# SMTP_SERVER = 'in-v3.mailjet.com'
# SMTP_PORT = 465
# SMTP_USERNAME = 'ecc9fbb1287fb704646f105e41957b98'
# SMTP_PASSWORD = '94ac02f9675203380d34e6a9c2fb4117'
# SMTP_USERNAME = 'MS_UUbVe5@trial-z3m5jgr0ykmgdpyo.mlsender.net'

MAILJET_API_KEY = 'ecc9fbb1287fb704646f105e41957b98'
MAILJET_SECRET_KEY = '6ebbe4977cbf45ed6c9601351451615a'
FROM_EMAIL = "v2gsol.dev@gmail.com"
