import os
from django.utils.log import DEFAULT_LOGGING
import logging.config

LOG_DIR = os.path.join(os.path.abspath('.'), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Disable Django's logging setup
LOGGING_CONFIG = None

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()



logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'server.log'),
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        # console logs to stderr
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'localhost',
            'port': 5959,
            'version': 1,
            'message_type': 'django',
            'fqdn': False,
            'tags': ['django.request'],
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console', 'logstash'],
        },
        'authentication': {
            'level': LOGLEVEL,
            'handlers': ['console', 'logstash'],
            'propagate': False,
        },
        'axes':  {
            'level': 'WARNING',
            'handlers': [],
            'propagate': False,
        },
        'noisy_module': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
        'django.request': {
            'handlers': ['console', 'logstash'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
})