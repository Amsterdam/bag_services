import re
from .settings import *


def _get_docker_host():
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return '0.0.0.0'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'atlas'),
        'USER': os.getenv('DATABASE_USER', 'atlas'),
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
        'slack': {
            'format': '%(message)s',
        },
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
        # Debug all batch jobs
        'batch': {
            'handlers': ['console'],
            'level': 'INFO',
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

        'urllib3.connectionpool': {
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

STATIC_ROOT = '/static/'

ELASTIC_SEARCH_HOSTS = ["{}:{}".format(
    os.getenv('ELASTICSEARCH_PORT_9200_TCP_ADDR', _get_docker_host()),
    os.getenv('ELASTICSEARCH_PORT_9200_TCP_PORT', 9200))]

DIVA_DIR = '/app/diva/'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.localdomain',
    '.datapunt.amsterdam.nl',
    'bag-api.service.consul',
    '.amsterdam.nl',
]

secret_key = os.getenv('DJANGO_SECRET_KEY')
SECRET_KEY = secret_key if secret_key else SECRET_KEY

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')   # Generate https links

CSRF_COOKIE_SECURE = True

print("Debug: %s" % DEBUG)
