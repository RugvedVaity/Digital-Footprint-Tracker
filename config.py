import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # Database - Support both SQLite and PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    if database_url and 'postgresql' in database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Default to SQLite for development
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///digital_footprint.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Flask-Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@digitalfootprint.com')

    # Flask-Limiter
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_PER_MINUTE = int(os.getenv('RATELIMIT_PER_MINUTE', 10))
    RATELIMIT_PER_HOUR = int(os.getenv('RATELIMIT_PER_HOUR', 100))

    # Application Settings
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 100))
    CACHE_EXPIRATION_HOURS = int(os.getenv('CACHE_EXPIRATION_HOURS', 1))
    DEFAULT_TIMEOUT_SECONDS = int(os.getenv('DEFAULT_TIMEOUT_SECONDS', 5))

    # Proxy Settings
    USE_PROXY = os.getenv('USE_PROXY', 'False').lower() == 'true'
    PROXY_LIST = os.getenv('PROXY_LIST', '').split(',') if os.getenv('PROXY_LIST') else []

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False

# Get config based on environment
config_name = os.getenv('FLASK_ENV', 'development').lower()
if config_name == 'production':
    config = ProductionConfig
elif config_name == 'testing':
    config = TestingConfig
else:
    config = DevelopmentConfig
