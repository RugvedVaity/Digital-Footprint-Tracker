import requests
import re
from abc import ABC, abstractmethod
from logger import logger

class BaseDetector(ABC):
    """Base class for detection methods"""

    def __init__(self, timeout=5):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    @abstractmethod
    def detect(self, url):
        """Detect if username exists - returns tuple (found: bool, reason: str)"""
        pass

    def _make_request(self, url):
        """Make HTTP request and return response"""
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers, allow_redirects=True)
            return response
        except requests.Timeout:
            raise Exception(f"Request timeout for {url}")
        except requests.RequestException as e:
            raise Exception(f"Request failed for {url}: {str(e)}")


class StatusCodeDetector(BaseDetector):
    """Detect based on HTTP status code"""

    def detect(self, url):
        """
        Return True if status code is 200, False for 404 or others
        """
        try:
            response = self._make_request(url)

            if response.status_code == 200:
                return True, "Found (200 OK)"
            elif response.status_code == 404:
                return False, "Not found (404)"
            elif response.status_code == 301 or response.status_code == 302:
                # Redirect - might indicate found or not found, check final URL
                if 'username' not in response.url.lower() and url != response.url:
                    return False, f"Redirected (status {response.status_code})"
                return True, f"Found with redirect (status {response.status_code})"
            elif response.status_code == 429:
                return None, "Rate limited (429) - please retry later"
            elif response.status_code == 403:
                return None, "Forbidden (403) - access denied"
            else:
                return None, f"Unknown status code ({response.status_code})"
        except Exception as e:
            logger.warning(f"StatusCodeDetector error: {str(e)}")
            return None, f"Error during detection: {str(e)}"


class ContentDetector(BaseDetector):
    """Detect based on page content patterns"""

    NOT_FOUND_PATTERNS = [
        r'page not found',
        r'user not found',
        r'does not exist',
        r'404',
        r'not available',
        r'no content',
        r'sorry.*not found'
    ]

    def detect(self, url):
        """
        Return True if page content indicates user exists
        """
        try:
            response = self._make_request(url)

            if response.status_code in [404, 410]:
                return False, "404 Not Found"

            if response.status_code not in [200, 201]:
                return None, f"Unexpected status code: {response.status_code}"

            content = response.text.lower()

            # Check for 404 keywords
            for pattern in self.NOT_FOUND_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    return False, f"Not found (keyword match: {pattern})"

            # If passes all 404 checks and got 200, likely found
            return True, "Found (content check)"

        except Exception as e:
            logger.warning(f"ContentDetector error: {str(e)}")
            return None, f"Error during detection: {str(e)}"


class AdvancedDetector(BaseDetector):
    """Advanced detection combining multiple strategies"""

    def __init__(self, timeout=5):
        super().__init__(timeout)
        self.status_detector = StatusCodeDetector(timeout)
        self.content_detector = ContentDetector(timeout)

    def detect(self, url):
        """
        Use multiple detection methods and combine results
        """
        try:
            # Try status code first (fastest)
            status_found, status_reason = self.status_detector.detect(url)

            # If status code is definitive, return it
            if status_found is not None:
                return status_found, status_reason

            # If status code is ambiguous, try content detection
            content_found, content_reason = self.content_detector.detect(url)
            return content_found, content_reason

        except Exception as e:
            logger.error(f"AdvancedDetector error: {str(e)}")
            return None, f"Detection error: {str(e)}"


# Factory function for creating detectors
def get_detector(detection_type='status_code', timeout=5):
    """
    Get appropriate detector based on type

    Args:
        detection_type: 'status_code', 'content', or 'advanced'
        timeout: Request timeout in seconds

    Returns:
        Detector instance
    """
    if detection_type == 'content':
        return ContentDetector(timeout)
    elif detection_type == 'advanced':
        return AdvancedDetector(timeout)
    else:
        return StatusCodeDetector(timeout)
