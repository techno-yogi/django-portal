import pytest
from django.urls import reverse
from django.test import Client

@pytest.fixture
def client():
    return Client()

def test_hello_world(client):
    response = client.get(reverse('hello_world'))
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello, World!'}
