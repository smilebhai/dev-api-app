import pytest
from os import environ
from tasks import add_numbers, ping

broker_url = environ.get('CELERY_BROKER_URL')
result_backend = environ.get('CELERY_BACKEND')


@pytest.fixture(scope='session')
def celery_config():
    return {
        "broker_url": broker_url,
        "result_backend": result_backend
    }

@pytest.mark.celery(result_backend=result_backend)
def test_add_numbers():
    assert add_numbers.delay(1,2).get(timeout=10) == 3

@pytest.mark.celery(result_backend=result_backend)
def test_ping():
    key = 'success'
    result = ping.delay('8.8.8.8').get(timeout=30)
    assert key in result
