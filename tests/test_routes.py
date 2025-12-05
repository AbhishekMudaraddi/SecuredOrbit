"""
Test cases for main routes (index, login, register, dashboard)
"""
import pytest
import os
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    # Set required environment variables for testing
    os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
    os.environ['AWS_REGION'] = 'us-east-1'
    os.environ['DYNAMODB_USERS_TABLE'] = 'PasswordManagerV2-Users-Test'
    os.environ['DYNAMODB_PASSWORDS_TABLE'] = 'PasswordManagerV2-Passwords-Test'
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test that index route returns 200 OK"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Secured Orbit' in response.data or b'password' in response.data.lower()


def test_register_get_route(client):
    """Test that register page loads (GET request)"""
    response = client.get('/register')
    assert response.status_code == 200


def test_login_get_route(client):
    """Test that login page loads (GET request)"""
    response = client.get('/login')
    assert response.status_code == 200


def test_dashboard_route_redirects_when_not_logged_in(client):
    """Test that dashboard redirects to login when not authenticated"""
    response = client.get('/dashboard', follow_redirects=False)
    # Should redirect to login (302) or return 401/403
    assert response.status_code in [302, 401, 403]


def test_logout_route_redirects(client):
    """Test that logout route redirects"""
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302  # Redirect


def test_forgot_password_get_route(client):
    """Test that forgot password page loads (GET request)"""
    response = client.get('/forgot-password')
    assert response.status_code == 200

