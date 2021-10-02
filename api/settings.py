from os import environ

# Flask settings
FLASK_DEBUG = True  # Do not use debug mode in production
FLASK_ENV = environ.get('FLASK_ENV', 'development')

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_MASK_SWAGGER = False
RESTX_ERROR_404_HELP = False

RATE_LIMITS = ['200 per day', '50 per hour', '20 per minute']
PING = 'PING'
RDAP = 'RDAP'
SERVICES = [PING, RDAP]

# Celery settings
CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL')
CELERY_BACKEND = environ.get('CELERY_BACKEND')

# Auth
TOKEN = environ.get('TOKEN')

# Host
IP = 'IP'
DOMAIN = 'DOMAIN'

SAMPLE_APIKEY = \
    'enteryourvirustotalkeyhere'
SAMPLE_DOMAIN = 'GOOGLE.COM'
SAMPLE_IP = '1.1.1.1'
