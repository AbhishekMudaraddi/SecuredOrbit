"""
Tests for health endpoint
"""
import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SESSION_SECRET'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health endpoint returns ok"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'ok': True}


def test_health_endpoint_method_not_allowed(client):
    """Test health endpoint only accepts GET"""
    response = client.post('/health')
    assert response.status_code == 405  # Method Not Allowed

