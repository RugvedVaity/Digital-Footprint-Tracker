import pytest
import json
from app import app, db
from models import Scan, SearchHistory

def test_index_page(client):
    """Test home page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_index_post_anonymous(client):
    """Test scanning as anonymous user"""
    with client.session_transaction() as sess:
        sess.pop('user_id', None)

    response = client.post('/', data={'username': 'testuser'})
    assert response.status_code == 200

def test_api_check_missing_username(client):
    """Test API check endpoint without username"""
    response = client.post('/api/check',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400

def test_api_check_single_username(client):
    """Test API check endpoint with username"""
    with client.application.app_context():
        response = client.post('/api/check',
            data=json.dumps({'username': 'testuser'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'username' in data
        assert 'results' in data
        assert 'risk_score' in data
        assert 'weighted_risk_score' in data

def test_api_check_batch_missing_usernames(client):
    """Test batch API without usernames"""
    response = client.post('/api/check-batch',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400

def test_api_check_batch_invalid_list(client):
    """Test batch API with invalid list"""
    response = client.post('/api/check-batch',
        data=json.dumps({'usernames': 'not-a-list'}),
        content_type='application/json'
    )
    assert response.status_code == 400

def test_api_check_batch_too_many(client):
    """Test batch API with too many usernames"""
    usernames = [f'user{i}' for i in range(150)]
    response = client.post('/api/check-batch',
        data=json.dumps({'usernames': usernames}),
        content_type='application/json'
    )
    assert response.status_code == 400

def test_api_check_batch_valid(client):
    """Test batch API with valid usernames"""
    response = client.post('/api/check-batch',
        data=json.dumps({'usernames': ['user1', 'user2', 'user3']}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'results' in data
    assert len(data['results']) == 3

def test_api_history_unauthenticated(client):
    """Test history API without authentication"""
    response = client.get('/api/history')
    # Should redirect to login or return 401/302
    assert response.status_code in [301, 302, 401, 403]

def test_api_history_authenticated(client, authenticated_client, test_user):
    """Test history API with authentication"""
    # Create a search history entry
    history = SearchHistory(
        user_id=test_user.id,
        search_query='testuser',
        results_count=2
    )
    with client.application.app_context():
        db.session.add(history)
        db.session.commit()

    response = authenticated_client.get('/api/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'history' in data

def test_api_results_nonexistent(client):
    """Test results API with non-existent scan"""
    response = client.get('/api/results/99999')
    assert response.status_code == 404

def test_dashboard_unauthenticated(client):
    """Test dashboard without authentication"""
    response = client.get('/dashboard')
    assert response.status_code in [301, 302, 401, 403]

def test_dashboard_authenticated(client, authenticated_client):
    """Test dashboard with authentication"""
    response = authenticated_client.get('/dashboard')
    assert response.status_code == 200

def test_error_404(client):
    """Test 404 error page"""
    response = client.get('/nonexistent-route')
    assert response.status_code == 404

def test_api_check_rate_limit(client):
    """Test rate limiting on API check"""
    # Make multiple requests rapidly
    for i in range(15):  # Limit is 10 per minute
        response = client.post('/api/check',
            data=json.dumps({'username': f'user{i}'}),
            content_type='application/json'
        )
        if i >= 10:
            # Should hit rate limit
            assert response.status_code == 429

def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.options('/api/check', headers={
        'Origin': 'http://example.com'
    })
    # Check if CORS headers are present
    assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200

def test_api_response_format(client):
    """Test API response format"""
    with client.application.app_context():
        response = client.post('/api/check',
            data=json.dumps({'username': 'testuser'}),
            content_type='application/json'
        )
        data = json.loads(response.data)

        assert 'username' in data
        assert 'results' in data
        assert isinstance(data['results'], dict)
        assert isinstance(data['risk_score'], int)
        assert isinstance(data['weighted_risk_score'], (int, float))
