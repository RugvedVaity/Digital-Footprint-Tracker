import pytest
from app import db
from models import User, Scan, SearchHistory
from datetime import datetime, timedelta

def test_user_creation(app_context):
    """Test user model creation"""
    user = User(username='john_doe', email='john@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.username == 'john_doe'
    assert user.email == 'john@example.com'
    assert user.check_password('password123')
    assert not user.check_password('wrongpass')

def test_user_password_hashing(app_context):
    """Test password hashing"""
    user = User(username='alice', email='alice@example.com')
    user.set_password('secure_password')

    # password should be hashed
    assert user.password_hash != 'secure_password'
    assert user.check_password('secure_password')
    assert not user.check_password('incorrect_password')

def test_scan_creation(app_context, test_user):
    """Test scan model creation"""
    results = {
        'GitHub': {'found': True, 'severity': 'medium'},
        'Twitter': {'found': False, 'severity': 'high'}
    }

    scan = Scan(
        username='testuser',
        results=results,
        risk_score=50,
        weighted_risk_score=55.5,
        platforms_found_count=1,
        total_platforms_checked=2,
        user_id=test_user.id
    )
    db.session.add(scan)
    db.session.commit()

    assert scan.id is not None
    assert scan.username == 'testuser'
    assert scan.risk_score == 50
    assert len(scan.results) == 2

def test_scan_cache_validity(app_context, test_user):
    """Test scan cache expiration"""
    results = {'GitHub': {'found': True, 'severity': 'medium'}}

    scan = Scan(
        username='testuser',
        results=results,
        risk_score=50,
        weighted_risk_score=55.5,
        platforms_found_count=1,
        total_platforms_checked=1,
        user_id=test_user.id,
        cache_hours=1
    )
    db.session.add(scan)
    db.session.commit()

    # Should be cached
    assert scan.is_cached()

    # Manually expire the cache
    scan.expires_at = datetime.utcnow() - timedelta(hours=1)
    assert not scan.is_cached()

def test_search_history_creation(app_context, test_user):
    """Test search history model"""
    history = SearchHistory(
        user_id=test_user.id,
        search_query='testuser',
        results_count=2
    )
    db.session.add(history)
    db.session.commit()

    assert history.id is not None
    assert history.search_query == 'testuser'
    assert history.results_count == 2

def test_scan_to_dict(app_context, test_user):
    """Test scan to_dict method"""
    results = {'GitHub': {'found': True, 'severity': 'medium'}}
    scan = Scan(
        username='testuser',
        results=results,
        risk_score=50,
        weighted_risk_score=55.5,
        platforms_found_count=1,
        total_platforms_checked=1,
        user_id=test_user.id
    )
    db.session.add(scan)
    db.session.commit()

    scan_dict = scan.to_dict()
    assert scan_dict['username'] == 'testuser'
    assert scan_dict['risk_score'] == 50
    assert scan_dict['weighted_risk_score'] == 55.5

def test_user_relationships(app_context, test_user):
    """Test user relationships with scans and history"""
    # Create scans
    results = {'GitHub': {'found': True, 'severity': 'medium'}}
    scan1 = Scan(
        username='user1',
        results=results,
        risk_score=50,
        weighted_risk_score=55.5,
        platforms_found_count=1,
        total_platforms_checked=1,
        user_id=test_user.id
    )
    scan2 = Scan(
        username='user2',
        results=results,
        risk_score=25,
        weighted_risk_score=30.0,
        platforms_found_count=1,
        total_platforms_checked=2,
        user_id=test_user.id
    )
    db.session.add(scan1)
    db.session.add(scan2)
    db.session.commit()

    # Check relationships
    assert len(test_user.scans) == 2
    assert test_user.scans[0].username == 'user1'
    assert test_user.scans[1].username == 'user2'
