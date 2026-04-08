import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    """Configure logging for the application"""

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create logger
    logger = logging.getLogger('digital_footprint')
    logger.setLevel(logging.DEBUG)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Export logger instance
logger = logging.getLogger('digital_footprint')

def log_scan(username, platforms_found, risk_score):
    """Log a scan operation"""
    logger.info(f"Scan completed for username '{username}': Found on {platforms_found} platforms, Risk score: {risk_score}%")

def log_user_action(user_id, action, details=''):
    """Log user actions"""
    logger.info(f"User {user_id} action: {action} {details}")

def log_api_call(endpoint, method, status_code):
    """Log API calls"""
    logger.info(f"API call - {method} {endpoint} - Status: {status_code}")

def log_error(error_msg, error_type='ERROR'):
    """Log errors"""
    logger.error(f"{error_type}: {error_msg}")

def log_warning(warning_msg):
    """Log warnings"""
    logger.warning(warning_msg)
