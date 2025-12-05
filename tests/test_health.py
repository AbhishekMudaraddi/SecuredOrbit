"""
Test cases for health check endpoint
"""
import pytest
import os
import sys

# Set environment variables BEFORE importing app
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['DYNAMODB_USERS_TABLE'] = 'PasswordManagerV2-Users-Test'
os.environ['DYNAMODB_PASSWORDS_TABLE'] = 'PasswordManagerV2-Passwords-Test'
os.environ['AWS_ACCESS_KEY_ID'] = 'test-access-key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret-key'

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app AFTER setting environment variables
import app as app_module
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test that health endpoint returns 200 OK"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data['ok'] is True


def test_health_endpoint_content_type(client):
    """Test that health endpoint returns JSON content type"""
    response = client.get('/health')
    assert response.status_code == 200
    assert 'application/json' in response.content_type

