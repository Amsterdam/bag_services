import re
from .settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv('DATABASE_PORT_5432_TCP_ADDR'),
        'PORT': os.getenv('DATABASE_PORT_5432_TCP_PORT', 5432),
        'CONN_MAX_AGE': 60,
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'loggers': {
    },
}

ELASTIC_SEARCH_HOSTS = ["{}:{}".format(os.getenv('ELASTICSEARCH_PORT_9200_TCP_ADDR'),
                                       os.getenv('ELASTICSEARCH_PORT_9200_TCP_PORT', 9200))]

PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
DIVA_DIR = os.path.abspath(os.path.join(PROJECT_DIR, 'atlas_import', 'diva'))

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', False)
