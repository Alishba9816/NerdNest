# tests/test_auth.py
"""
Tests for authentication endpoints (register, login)
Tests both successful cases and error cases
"""
import pytest


# ============= REGISTRATION TESTS =============

def test_register_success(client):
    """
    Test successful user registration
    ARRANGE: Valid registration data
    ACT: POST to /api/auth/register
    ASSERT: Status 201, success message returned
    """
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword123'
    })
    
    assert response.status_code == 201
    assert response.json['message'] == 'Account created successfully!'


def test_register_missing_username(client):
    """
    Test registration fails without username
    """
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'required' in response.json['error'].lower()


def test_register_missing_email(client):
    """
    Test registration fails without email
    """
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    assert 'error' in response.json


def test_register_missing_password(client):
    """
    Test registration fails without password
    """
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    
    assert response.status_code == 400
    assert 'error' in response.json


def test_register_duplicate_username(client, test_user):
    """
    Test registration fails with existing username
    test_user fixture already creates a user with username='testuser'
    """
    response = client.post('/api/auth/register', json={
        'username': 'testuser',  # Already exists
        'email': 'different@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error'].lower()


def test_register_duplicate_email(client, test_user):
    """
    Test registration fails with existing email
    """
    response = client.post('/api/auth/register', json={
        'username': 'differentuser',
        'email': 'test@example.com',  # Already exists
        'password': 'password123'
    })
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error'].lower()


def test_register_no_json_data(client):
    """
    Test registration fails when no JSON data is sent
    """
    response = client.post('/api/auth/register')
    
    assert response.status_code == 415


# ============= LOGIN TESTS =============

def test_login_success(client, test_user):
    """
    Test successful login with correct credentials
    Should return access_token and refresh_token
    """
    response = client.post('/api/auth/login', json={
        'username': test_user['username'],
        'password': test_user['password']
    })
    
    assert response.status_code == 200
    assert 'message' in response.json
    assert 'Login successful' in response.json['message']
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json
    
    # Tokens should be non-empty strings
    assert len(response.json['access_token']) > 0
    assert len(response.json['refresh_token']) > 0


def test_login_wrong_password(client, test_user):
    """
    Test login fails with incorrect password
    """
    response = client.post('/api/auth/login', json={
        'username': test_user['username'],
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert 'error' in response.json
    assert 'invalid' in response.json['error'].lower()


def test_login_nonexistent_user(client):
    """
    Test login fails for user that doesn't exist
    """
    response = client.post('/api/auth/login', json={
        'username': 'nonexistentuser',
        'password': 'password123'
    })
    
    assert response.status_code == 401
    assert 'error' in response.json


def test_login_missing_username(client):
    """
    Test login fails without username
    """
    response = client.post('/api/auth/login', json={
        'password': 'password123'
    })
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'required' in response.json['error'].lower()


def test_login_missing_password(client):
    """
    Test login fails without password
    """
    response = client.post('/api/auth/login', json={
        'username': 'testuser'
    })
    
    assert response.status_code == 400
    assert 'error' in response.json


def test_login_empty_credentials(client):
    """
    Test login fails with empty strings
    """
    response = client.post('/api/auth/login', json={
        'username': '',
        'password': ''
    })
    
    assert response.status_code == 400


def test_login_no_json_data(client):
    """
    Test login fails when no JSON data is sent
    """
    response = client.post('/api/auth/login')
    
    assert response.status_code == 415


# ============= TOKEN TESTS =============

def test_protected_route_without_token(client):
    """
    Test that protected routes reject requests without JWT token
    Using dashboard as example
    """
    response = client.get('/dashboard')
    
    assert response.status_code == 401


def test_protected_route_with_valid_token(client, auth_headers):
    """
    Test that protected routes accept requests with valid JWT token
    """
    response = client.get('/dashboard', headers=auth_headers)
    
    # Should not be 401 (unauthorized)
    assert response.status_code != 401


def test_protected_route_with_invalid_token(client):
    """
    Test that protected routes reject requests with invalid JWT token
    """
    response = client.get('/dashboard', headers={
        'Authorization': 'Bearer invalid_token_here'
    })
    
    assert response.status_code == 422  # JWT error


# ============= EDGE CASES =============

@pytest.mark.parametrize('username,email,password', [
    ('a', 'test@example.com', 'pass'),  # Very short username
    ('user' * 100, 'test@example.com', 'pass'),  # Very long username
    ('testuser', 'notanemail', 'pass'),  # Invalid email format
    ('testuser', 'test@example.com', ''),  # Empty password
])
def test_register_edge_cases(client, username, email, password):
    """
    Test registration with various edge cases
    Using parametrize to test multiple scenarios with one test
    """
    response = client.post('/api/auth/register', json={
        'username': username,
        'email': email,
        'password': password
    })
    
    # Should either succeed or fail gracefully (not crash)
    assert response.status_code in [200, 201, 400, 422]


def test_case_sensitive_username(client, test_user):
    """
    Test if usernames are case-sensitive
    Depending on your requirements, adjust assertions
    """
    # Try to login with different case
    response = client.post('/api/auth/login', json={
        'username': test_user['username'].upper(),  # TESTUSER instead of testuser
        'password': test_user['password']
    })
    
    # Document behavior: should this work or fail?
    # Adjust based on your requirements
    assert response.status_code in [200, 401]


# ============= SECURITY TESTS =============

def test_password_is_hashed(app, client):
    """
    Test that passwords are stored hashed, not in plain text
    """
    from app.models.user import User
    from app.extensions import db
    
    # Register a user
    client.post('/api/auth/register', json={
        'username': 'securitytest',
        'email': 'security@example.com',
        'password': 'mysecretpassword'
    })
    
    # Check database directly
    with app.app_context():
        user = User.query.filter_by(username='securitytest').first()
        
        # Password should NOT be stored as plain text
        assert user.password != 'mysecretpassword'
        
        # Password should be a hash (starts with bcrypt identifier)
        assert user.password.startswith('$2b$')


def test_sql_injection_prevention(client):
    """
    Test that SQL injection attempts don't work
    """
    response = client.post('/api/auth/login', json={
        'username': "admin' OR '1'='1",
        'password': "password' OR '1'='1"
    })
    
    # Should fail, not allow injection
    assert response.status_code == 401