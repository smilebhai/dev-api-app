import pytest
from flask import current_app
import time
from routes.services import service_available

from app import flask_app as app

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():  # New!!
            assert current_app.config["FLASK_ENV"] == "development"
        yield client


def test_service_available():
    sample_services = ['ping', 'PING', 'pInG', 'rdap', 'RDAP', 'RdAp']
    for service in sample_services:
        assert service_available(service)


def test_service_not_available():
    sample_services = ['junk', 'pong', '']
    for service in sample_services:
        assert not service_available(service)


def test_swagger_settings(client):
    url = '/api/swagger.json'  # The root url of the Swagger docs
    response = client.get(url)
    # Assumes that it will return a 200 response
    assert response.status_code == 200


def test_lookupservice(client):
    url = '/api/services/default/8.8.8.8'
    key = b'services'
    headers = {
        'X-API-KEY': 'mytoken'
    }
    data = {
        'services': ['ping', 'rdap', 'junk']
    }
    response = client.post(url, json=data, headers=headers)
    # Assumes that it will return a 200 response
    assert response.status_code == 200
    assert key in response.data


def test_lookupservice_invalid_domain(client):
    url = '/api/services/default/1.1.1.11111'
    key = b'invalid'
    headers = {
        'X-API-KEY': 'mytoken'
    }
    data = {
        'services': ['ping']
    }
    response = client.post(url, json=data, headers=headers)
    # Assumes that it will return a 200 response
    assert response.status_code == 200
    assert key in response.data


def test_lookupservice_missing_token(client):
    url = '/api/services/default/8.8.8.8'
    key = b'missing'
    headers = {}
    data = {
        'services': ['ping']
    }
    response = client.post(url, json=data, headers=headers)
    assert response.status_code == 401  # Error: UNAUTHORIZED
    assert key in response.data


def test_lookupservice_incorrect_token(client):
    url = '/api/services/default/8.8.8.8'
    key = b'incorrect'
    headers = {
        'X-API-KEY': 'notmytoken'
    }
    data = {
        'services': ['ping']
    }
    response = client.post(url, json=data, headers=headers)
    assert response.status_code == 401  # Error: UNAUTHORIZED
    assert key in response.data


def test_rate_limit_endpoint(client):
    url = '/api/ratelimit/test'  # The test endpoint
    message = b'exceeded'
    response = client.get(url)
    while response.status_code == 200:
        time.sleep(1)
        response = client.get(url)
    assert response.status_code == 429  # HTTP 429 Too Many Requests
    assert message in response.data
