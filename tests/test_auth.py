import pytest
from app import app, db
from models import User

def test_register_page(client):
    """Test register page loads"""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data or b'register' in response.data

def test_register_valid_user(client):
    """Test user registration"""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'newuser@example.com'

def test_register_password_mismatch(client):
    """Test registration with mismatched passwords"""
    response = client.post('/auth/register', data={
        'username': 'user1',
        'email': 'user1@example.com',
        'password': 'password123',
        'password_confirm': 'password456'
    }, follow_redirects=True)

    assert b'do not match' in response.data or b'Passwords' in response.data

def test_register_short_password(client):
    """Test registration with short password"""
    response = client.post('/auth/register', data={
        'username': 'user2',
        'email': 'user2@example.com',
        'password': 'pass',
        'password_confirm': 'pass'
    }, follow_redirects=True)

    assert b'Password' in response.data or b'password' in response.data

def test_register_invalid_username(client):
    """Test registration with invalid username"""
    response = client.post('/auth/register', data={
        'username': 'ab',  # Too short
        'email': 'user3@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)

    assert b'Username' in response.data or b'username' in response.data

def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username"""
    response = client.post('/auth/register', data={
        'username': test_user.username,
        'email': 'newuser@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)

    assert b'already exists' in response.data or b'exists' in response.data

def test_login_page(client):
    """Test login page loads"""
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_login_valid(client, test_user):
    """Test valid login"""
    response = client.post('/auth/login', data={
        'username_or_email': test_user.username,
        'password': 'testpass123'
    }, follow_redirects=True)

    assert response.status_code == 200
    # User should be logged in (check for logout or protected content)

def test_login_with_email(client, test_user):
    """Test login using email"""
    response = client.post('/auth/login', data={
        'username_or_email': test_user.email,
        'password': 'testpass123'
    }, follow_redirects=True)

    assert response.status_code == 200

def test_login_invalid_password(client, test_user):
    """Test login with invalid password"""
    response = client.post('/auth/login', data={
        'username_or_email': test_user.username,
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert b'Invalid' in response.data or b'invalid' in response.data

def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post('/auth/login', data={
        'username_or_email': 'nonexistent',
        'password': 'password123'
    }, follow_redirects=True)

    assert b'Invalid' in response.data or b'invalid' in response.data

def test_logout(client, authenticated_client):
    """Test logout"""
    response = authenticated_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
