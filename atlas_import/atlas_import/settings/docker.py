import re
from .settings import *


def _get_docker_host():
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return 'localhost'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'atlas'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv('DATABASE_PORT_5432_TCP_ADDR', _get_docker_host()),
        'PORT': os.getenv('DATABASE_PORT_5432_TCP_PORT', 5434),
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
        'elasticsearch': {
            'level': 'WARNING',
            'handlers': ['console'],
        },

        'elasticsearch.trace': {
            'level': 'ERROR',
            'handlers': ['console'],
        },
    },
}

STATIC_ROOT = '/static/'

ELASTIC_SEARCH_HOSTS = ["{}:{}".format(
    os.getenv('ELASTICSEARCH_PORT_9200_TCP_ADDR', _get_docker_host()),
    os.getenv('ELASTICSEARCH_PORT_9200_TCP_PORT', 9200))]

PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
DIVA_DIR = os.path.abspath(os.path.join(PROJECT_DIR, 'atlas_import', 'diva'))

secret_key = os.getenv('DJANGO_SECRET_KEY')
SECRET_KEY = secret_key if secret_key else SECRET_KEY

DEBUG = os.getenv('DJANGO_DEBUG', False)
