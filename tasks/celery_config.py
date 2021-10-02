from os import environ

broker_url = environ.get('CELERY_BROKER_URL')
result_backend = environ.get('CELERY_BACKEND')
