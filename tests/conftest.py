import pytest
import os
import tempfile
from app import app, db
from models import User, Scan, SearchHistory

@pytest.fixture
def client():
    """Create test client"""
    # Create a temporary database
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def app_context():
    """Create application context"""
    with app.app_context():
        yield app

@pytest.fixture
def test_user():
    """Create a test user"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpass123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client"""
    from flask_login import login_user
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
    return client
