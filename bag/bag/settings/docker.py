
from .settings_common import *  # noqa
from .settings import *  # noqa

WSGI_APPLICATION = 'bag.wsgi'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

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
            'level': 'DEBUG',
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

# DEBUG=False
STATIC_ROOT = '/static/'
STATIC_URL = '/gebieden/static/'

DIVA_DIR = '/app/data/'
GOB_DIR = '/app/data/gob/'

# Generate h ttps links
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
