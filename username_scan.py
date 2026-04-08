import json
import os
from time import sleep
from detection import get_detector
from logger import logger, log_scan, log_warning

# Load sites configuration
def load_sites_config():
    """Load sites configuration from JSON"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'sites.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Sites configuration not found at {config_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in sites configuration")
        return {}

# Load sites on module import
SITES_CONFIG = load_sites_config()

def check_username(username, timeout=5, detector_type='advanced', use_cache=None):
    """
    Check if username exists across configured platforms

    Args:
        username (str): Username to check
        timeout (int): Request timeout in seconds
        detector_type (str): Type of detector to use ('status_code', 'content', 'advanced')
        use_cache (callable): Optional function to get cached results

    Returns:
        tuple: (results_dict, risk_score, weighted_risk_score)
    """
    if not username or not isinstance(username, str):
        return {}, 0, 0

    username = username.strip()

    # Check cache if available
    if use_cache and callable(use_cache):
        cached_result = use_cache(username)
        if cached_result:
            logger.info(f"Using cached result for username: {username}")
            return cached_result

    detector = get_detector(detector_type, timeout)
    results = {}
    found_count = 0
    weighted_score = 0
    severity_weights = {'low': 1, 'medium': 2, 'high': 3}
    max_weighted_score = 0

    for site_name, site_config in SITES_CONFIG.items():
        url = site_config['url'].format(username=username)
        severity = site_config.get('severity', 'medium')
        weight = severity_weights.get(severity, 2)

        try:
            found, reason = detector.detect(url)

            results[site_name] = {
                'found': found if found is not None else False,
                'severity': severity,
                'reason': reason,
                'category': site_config.get('category', 'Other'),
                'icon': site_config.get('icon', 'link')
            }

            if found:
                found_count += 1
                weighted_score += weight

            max_weighted_score += weight

            # Small delay to avoid rate limiting
            sleep(0.1)

        except Exception as e:
            logger.error(f"Error checking {site_name}: {str(e)}")
            results[site_name] = {
                'found': False,
                'severity': severity,
                'reason': f"Error: {str(e)}",
                'category': site_config.get('category', 'Other'),
                'icon': site_config.get('icon', 'link')
            }

    # Calculate risk scores
    total_sites = len(SITES_CONFIG)
    risk_score = int((found_count / total_sites) * 100) if total_sites > 0 else 0
    weighted_risk_score = (weighted_score / max_weighted_score * 100) if max_weighted_score > 0 else 0

    log_scan(username, found_count, risk_score)

    return results, risk_score, weighted_risk_score


def check_usernames_batch(usernames, timeout=5, detector_type='advanced',
                          batch_delay=0.5, use_cache=None):
    """
    Check multiple usernames in batch

    Args:
        usernames (list): List of usernames to check
        timeout (int): Request timeout per username
        detector_type (str): Type of detector to use
        batch_delay (float): Delay between usernames in seconds
        use_cache (callable): Optional caching function

    Returns:
        list: List of (username, results, risk_score, weighted_risk_score) tuples
    """
    batch_results = []

    for i, username in enumerate(usernames):
        try:
            results, risk_score, weighted_risk_score = check_username(
                username, timeout, detector_type, use_cache
            )
            batch_results.append({
                'username': username,
                'results': results,
                'risk_score': risk_score,
                'weighted_risk_score': weighted_risk_score,
                'status': 'completed'
            })

            # Delay between requests
            if i < len(usernames) - 1:
                sleep(batch_delay)

        except Exception as e:
            logger.error(f"Error checking username {username}: {str(e)}")
            batch_results.append({
                'username': username,
                'results': {},
                'risk_score': 0,
                'weighted_risk_score': 0,
                'status': 'error',
                'error': str(e)
            })

    return batch_results


def get_platform_list():
    """Get list of all configured platforms"""
    return list(SITES_CONFIG.keys())


def get_platform_info(platform_name):
    """Get information about a specific platform"""
    return SITES_CONFIG.get(platform_name, None)


def get_platforms_by_severity(severity):
    """Get all platforms with a specific severity level"""
    return [
        name for name, config in SITES_CONFIG.items()
        if config.get('severity') == severity
    ]


def get_platforms_by_category(category):
    """Get all platforms in a specific category"""
    return [
        name for name, config in SITES_CONFIG.items()
        if config.get('category') == category
    ]