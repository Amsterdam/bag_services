"""
Django settings for atlas_import project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from django.conf import settings
from django.core import checks
import elasticsearch
import elasticsearch_dsl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

SECRET_KEY = 'k56a9)qv*%swsapf2)w4tjgjsjbs+fc83qq8!^13&usmlk3!5^'

DEBUG = False

# Application definition

INSTALLED_APPS = (
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',

    'django.contrib.staticfiles',
    'django_jenkins',

    'batch',
    'atlas',
    'atlas_jobs',
    'atlas_api',

    'django.contrib.gis',
    'rest_framework',
    'rest_framework_gis',
    'corsheaders',
)

MIDDLEWARE_CLASSES = (
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'atlas_import.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'atlas_import.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'atlas'
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

ALLOWED_HOSTS = [
    'localhost',
    '.localdomain',
    '.datalabamsterdam.nl',
]

REST_FRAMEWORK = dict(
    PAGE_SIZE=10,
)

CORS_ORIGIN_REGEX_WHITELIST = (
    '^(https?://)?localhost(:\d+)?$',
    '^(https?://)?.*\.datalabamsterdam\.nl$',
)

# Security

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

from .checks import *       # used for ./manage.py check

