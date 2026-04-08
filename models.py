from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and scan history"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scans = db.relationship('Scan', backref='user', lazy=True, cascade='all, delete-orphan')
    search_history = db.relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Scan(db.Model):
    """Scan model to store scan results"""
    __tablename__ = 'scans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    username = db.Column(db.String(120), nullable=False, index=True)
    results = db.Column(db.JSON, nullable=False)  # {platform: {'found': bool, 'severity': 'low'|'medium'|'high'}}
    risk_score = db.Column(db.Integer, nullable=False)  # 0-100
    weighted_risk_score = db.Column(db.Float, nullable=False)  # 0-100 with severity weight
    platforms_found_count = db.Column(db.Integer, nullable=False)
    total_platforms_checked = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)  # For cache expiration

    def __init__(self, username, results, risk_score, weighted_risk_score,
                 platforms_found_count, total_platforms_checked, user_id=None, cache_hours=1):
        self.user_id = user_id
        self.username = username
        self.results = results
        self.risk_score = risk_score
        self.weighted_risk_score = weighted_risk_score
        self.platforms_found_count = platforms_found_count
        self.total_platforms_checked = total_platforms_checked
        self.expires_at = datetime.utcnow() + timedelta(hours=cache_hours)

    def is_cached(self):
        """Check if scan result is still valid"""
        return datetime.utcnow() < self.expires_at

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'results': self.results,
            'risk_score': self.risk_score,
            'weighted_risk_score': self.weighted_risk_score,
            'platforms_found_count': self.platforms_found_count,
            'total_platforms_checked': self.total_platforms_checked,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_cached': self.is_cached()
        }

    def __repr__(self):
        return f'<Scan {self.username}>'


class SearchHistory(db.Model):
    """Search history model to track user searches"""
    __tablename__ = 'search_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=True, index=True)
    search_query = db.Column(db.String(120), nullable=False)
    results_count = db.Column(db.Integer, nullable=False)  # Number of platforms where username was found
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    scan = db.relationship('Scan', backref='history_entries')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'search_query': self.search_query,
            'results_count': self.results_count,
            'created_at': self.created_at.isoformat(),
            'scan_id': self.scan_id
        }

    def __repr__(self):
        return f'<SearchHistory {self.search_query}>'
