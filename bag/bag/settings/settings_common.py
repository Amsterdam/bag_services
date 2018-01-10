"""
Django settings for BAG services project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
insecure_key = 'insecure'
SECRET_KEY = os.getenv('BAG_SECRET_KEY', insecure_key)

DEBUG = SECRET_KEY == insecure_key

ALLOWED_HOSTS = ['*']

DATAPUNT_API_URL = os.getenv(
    'DATAPUNT_API_URL', 'https://api.data.amsterdam.nl/')


INTERNAL_IPS = ('127.0.0.1', '0.0.0.0')


# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',

    'django_filters',
    'django_extensions',
    'django.contrib.gis',

    'datapunt_api',  # custom api templates
    'search',        # search urls
    'batch',
    'bag_commands',
    'datasets.bag',
    'datasets.brk',
    'datasets.wkpb',
    'geo_views',
    'health',

    'rest_framework',
    'rest_framework_gis',
    'rest_framework_swagger',
]

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'authorization_django.authorization_middleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGSTASH_HOST = os.getenv('LOGSTASH_HOST', '127.0.0.1')
LOGSTASH_PORT = int(os.getenv('LOGSTASH_GELF_UDP_PORT', 12201))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'console': {
            'format': '{asctime} - {name} - {levelname} - {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },

        'graypy': {
            'level': 'ERROR',
            'class': 'graypy.GELFHandler',
            'host': LOGSTASH_HOST,
            'port': LOGSTASH_PORT,
        },

    },

    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'graypy'],
    },

    'loggers': {
        'django.db': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },

        # Debug all batch jobs
        'doc': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'index': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'batch': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

        'search': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

        'elasticsearch': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

        'urllib3': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

        'factory.containers': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },

        'factory.generate': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },

        'requests.packages.urllib3.connectionpool': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

        'elasticsearch_dsl': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

        # Log all unhandled exceptions
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

    },
}
