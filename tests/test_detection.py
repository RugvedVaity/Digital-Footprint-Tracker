import pytest
from detection import StatusCodeDetector, ContentDetector, AdvancedDetector, get_detector
from unittest.mock import Mock, patch, MagicMock
import requests

@pytest.fixture
def mock_response_200():
    """Mock successful response"""
    response = Mock()
    response.status_code = 200
    response.text = '<html>User Profile</html>'
    response.url = 'https://github.com/testuser'
    return response

@pytest.fixture
def mock_response_404():
    """Mock 404 response"""
    response = Mock()
    response.status_code = 404
    response.text = '<html>Page not found</html>'
    return response

def test_status_code_detector_found(mock_response_200):
    """Test status code detector with 200 response"""
    detector = StatusCodeDetector()

    with patch('detection.requests.get', return_value=mock_response_200):
        found, reason = detector.detect('https://github.com/testuser')
        assert found is True
        assert 'Found' in reason

def test_status_code_detector_not_found(mock_response_404):
    """Test status code detector with 404 response"""
    detector = StatusCodeDetector()

    with patch('detection.requests.get', return_value=mock_response_404):
        found, reason = detector.detect('https://github.com/testuser')
        assert found is False
        assert 'not found' in reason.lower()

def test_status_code_detector_timeout():
    """Test status code detector with timeout"""
    detector = StatusCodeDetector()

    with patch('detection.requests.get', side_effect=requests.Timeout):
        found, reason = detector.detect('https://github.com/testuser')
        assert found is None
        assert 'timeout' in reason.lower() or 'error' in reason.lower()

def test_content_detector_found(mock_response_200):
    """Test content detector with valid content"""
    detector = ContentDetector()

    with patch('detection.requests.get', return_value=mock_response_200):
        found, reason = detector.detect('https://reddit.com/user/testuser')
        assert found is True

def test_content_detector_not_found():
    """Test content detector with 404 keywords"""
    detector = ContentDetector()
    response = Mock()
    response.status_code = 200
    response.text = '<html>User not found. This page does not exist.</html>'

    with patch('detection.requests.get', return_value=response):
        found, reason = detector.detect('https://reddit.com/user/testuser')
        assert found is False

def test_advanced_detector(mock_response_200):
    """Test advanced detector"""
    detector = AdvancedDetector()

    with patch('detection.requests.get', return_value=mock_response_200):
        found, reason = detector.detect('https://github.com/testuser')
        assert found is True

def test_get_detector():
    """Test detector factory function"""
    detector1 = get_detector('status_code')
    assert isinstance(detector1, StatusCodeDetector)

    detector2 = get_detector('content')
    assert isinstance(detector2, ContentDetector)

    detector3 = get_detector('advanced')
    assert isinstance(detector3, AdvancedDetector)

    detector4 = get_detector('unknown')
    assert isinstance(detector4, StatusCodeDetector)  # Default

def test_detector_with_custom_timeout():
    """Test detector with custom timeout"""
    detector = StatusCodeDetector(timeout=10)
    assert detector.timeout == 10

def test_status_code_detector_rate_limit():
    """Test status code detector with rate limit response"""
    detector = StatusCodeDetector()
    response = Mock()
    response.status_code = 429
    response.text = '<html>Too many requests</html>'

    with patch('detection.requests.get', return_value=response):
        found, reason = detector.detect('https://github.com/testuser')
        assert found is None
        assert '429' in reason

def test_status_code_detector_redirect():
    """Test status code detector with redirect"""
    detector = StatusCodeDetector()
    response = Mock()
    response.status_code = 301
    response.url = 'https://redirect.example.com'

    with patch('detection.requests.get', return_value=response):
        found, reason = detector.detect('https://github.com/testuser')
        # Should be ambiguous
        assert found is not None  # Could be found or not found
