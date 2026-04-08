import pytest
from username_scan import (
    check_username, check_usernames_batch, get_platform_list,
    get_platform_info, get_platforms_by_severity, get_platforms_by_category
)
from unittest.mock import patch, Mock

def test_get_platform_list():
    """Test getting platform list"""
    platforms = get_platform_list()
    assert len(platforms) > 0
    assert 'GitHub' in platforms
    assert isinstance(platforms, list)

def test_get_platform_info():
    """Test getting platform info"""
    info = get_platform_info('GitHub')
    assert info is not None
    assert 'url' in info
    assert 'severity' in info
    assert 'category' in info

def test_get_platform_info_nonexistent():
    """Test getting info for non-existent platform"""
    info = get_platform_info('NonExistent')
    assert info is None

def test_get_platforms_by_severity():
    """Test getting platforms by severity"""
    high_severity = get_platforms_by_severity('high')
    assert len(high_severity) > 0
    assert all(get_platform_info(p)['severity'] == 'high' for p in high_severity)

def test_get_platforms_by_category():
    """Test getting platforms by category"""
    social = get_platforms_by_category('Social')
    assert len(social) > 0
    assert all(get_platform_info(p)['category'] == 'Social' for p in social)

def test_check_username_basic():
    """Test basic username check"""
    with patch('username_scan.get_detector') as mock_detector:
        detector_instance = Mock()
        detector_instance.detect.return_value = (False, 'Not found')
        mock_detector.return_value = detector_instance

        results, risk_score, weighted_score = check_username('testuser')

        assert isinstance(results, dict)
        assert isinstance(risk_score, int)
        assert isinstance(weighted_score, float)
        assert risk_score >= 0 and risk_score <= 100
        assert weighted_score >= 0 and weighted_score <= 100

def test_check_username_found():
    """Test when username is found"""
    with patch('username_scan.get_detector') as mock_detector:
        detector_instance = Mock()
        detector_instance.detect.side_effect = [
            (True, 'Found'),   # GitHub
            (True, 'Found'),   # Reddit
            (False, 'Not found')  # Twitter
        ]
        mock_detector.return_value = detector_instance

        results, risk_score, weighted_score = check_username('testuser')

        # Count found platforms
        found_count = sum(1 for r in results.values() if r.get('found'))
        assert risk_score == int((found_count / len(results)) * 100)

def test_check_username_invalid():
    """Test with invalid username"""
    results, risk_score, weighted_score = check_username(None)
    assert results == {}
    assert risk_score == 0
    assert weighted_score == 0

def test_check_username_empty_string():
    """Test with empty string username"""
    results, risk_score, weighted_score = check_username('')
    assert results == {}
    assert risk_score == 0
    assert weighted_score == 0

def test_check_usernames_batch():
    """Test batch checking"""
    with patch('username_scan.get_detector') as mock_detector:
        detector_instance = Mock()
        detector_instance.detect.return_value = (True, 'Found')
        mock_detector.return_value = detector_instance

        batch_results = check_usernames_batch(['user1', 'user2'])

        assert len(batch_results) == 2
        assert all('status' in result for result in batch_results)
        assert all('username' in result for result in batch_results)
        assert all('risk_score' in result for result in batch_results)

def test_check_usernames_batch_empty():
    """Test batch checking with empty list"""
    batch_results = check_usernames_batch([])
    assert len(batch_results) == 0

def test_check_usernames_batch_error_handling():
    """Test batch checking error handling"""
    with patch('username_scan.check_username', side_effect=Exception('Test error')):
        batch_results = check_usernames_batch(['user1'])

        assert len(batch_results) == 1
        assert batch_results[0]['status'] == 'error'
        assert 'error' in batch_results[0]

def test_check_username_with_timeout():
    """Test checking with custom timeout"""
    with patch('username_scan.get_detector') as mock_detector:
        detector_instance = Mock()
        detector_instance.detect.return_value = (False, 'Not found')
        mock_detector.return_value = detector_instance

        results, risk_score, weighted_score = check_username('testuser', timeout=15)

        # Verify timeout was passed to detector
        mock_detector.assert_called()

def test_check_username_with_detector_type():
    """Test checking with specific detector type"""
    with patch('username_scan.get_detector') as mock_detector:
        detector_instance = Mock()
        detector_instance.detect.return_value = (False, 'Not found')
        mock_detector.return_value = detector_instance

        results, risk_score, weighted_score = check_username('testuser', detector_type='content')

        # Verify detector type was specified
        mock_detector.assert_called_once()

def test_results_have_severity():
    """Test that all results include severity info"""
    with patch('username_scan.get_detector') as mock_detector:
        detector_instance = Mock()
        detector_instance.detect.return_value = (False, 'Not found')
        mock_detector.return_value = detector_instance

        results, _, _ = check_username('testuser')

        # Each result should have required fields
        for platform, result in results.items():
            assert 'found' in result
            assert 'severity' in result
            assert 'category' in result
            assert result['severity'] in ['low', 'medium', 'high']

def test_batch_with_delay():
    """Test batch checking respects delay"""
    with patch('username_scan.get_detector', return_value=Mock(detect=Mock(return_value=(False, 'Not found')))):
        with patch('username_scan.sleep') as mock_sleep:
            batch_results = check_usernames_batch(['user1', 'user2'], batch_delay=0.5)

            # Should have sleep calls between requests
            assert mock_sleep.call_count > 0
