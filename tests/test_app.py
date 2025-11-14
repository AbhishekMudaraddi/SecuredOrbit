"""
Basic application tests
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


def test_index_redirects_to_login(client):
    """Test index redirects to login when not authenticated"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location


def test_login_page_loads(client):
    """Test login page loads successfully"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower() or b'Login' in response.data


def test_register_page_loads(client):
    """Test register page loads successfully"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'register' in response.data.lower() or b'Register' in response.data


def test_logout_redirects(client):
    """Test logout redirects to login"""
    response = client.get('/logout')
    assert response.status_code == 302
    assert '/login' in response.location


def test_dashboard_requires_auth(client):
    """Test dashboard requires authentication"""
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.location

