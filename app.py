from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta

from config import config
from models import db, User, Scan, SearchHistory
from username_scan import check_username, check_usernames_batch
from logger import setup_logging, log_user_action, log_api_call
from mail_service import mail
from auth import auth_bp
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)

# Initialize extensions
db.init_app(app)
mail.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Register blueprints
app.register_blueprint(auth_bp)

# Setup logging
logger = setup_logging(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def before_request():
    """Create database tables if they don't exist"""
    try:
        db.create_all()
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        # Don't crash the app if DB fails, just log it

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    risk_score = 0
    weighted_risk_score = 0
    is_authenticated = current_user.is_authenticated

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            try:
                # Check username
                results, risk_score, weighted_risk_score = check_username(username)

                # Save scan to database if user is logged in
                if is_authenticated:
                    cache_hours = 1  # From config
                    scan = Scan(
                        username=username,
                        results=results,
                        risk_score=risk_score,
                        weighted_risk_score=weighted_risk_score,
                        platforms_found_count=sum(1 for r in results.values() if r.get('found')),
                        total_platforms_checked=len(results),
                        user_id=current_user.id,
                        cache_hours=cache_hours
                    )
                    db.session.add(scan)

                    # Add to search history
                    platforms_found = sum(1 for r in results.values() if r.get('found'))
                    search_history = SearchHistory(
                        user_id=current_user.id,
                        scan_id=scan.id,
                        search_query=username,
                        results_count=platforms_found
                    )
                    db.session.add(search_history)
                    db.session.commit()

                    log_user_action(current_user.id, 'scan', f"username: {username}")

            except Exception as e:
                logger.error(f"Error during scan: {str(e)}")

    return render_template(
        'index.html',
        results=results,
        risk_score=risk_score,
        weighted_risk_score=weighted_risk_score,
        is_authenticated=is_authenticated
    )


@app.route('/api/check', methods=['POST'])
@limiter.limit("10 per minute")
def api_check():
    """API endpoint to check single username"""
    data = request.get_json()
    username = data.get('username', '').strip()

    if not username:
        log_api_call('/api/check', 'POST', 400)
        return jsonify({'error': 'Username required'}), 400

    try:
        results, risk_score, weighted_risk_score = check_username(username)

        # Save to database if authenticated
        if current_user.is_authenticated:
            scan = Scan(
                username=username,
                results=results,
                risk_score=risk_score,
                weighted_risk_score=weighted_risk_score,
                platforms_found_count=sum(1 for r in results.values() if r.get('found')),
                total_platforms_checked=len(results),
                user_id=current_user.id
            )
            db.session.add(scan)
            db.session.commit()

        log_api_call('/api/check', 'POST', 200)
        return jsonify({
            'username': username,
            'results': results,
            'risk_score': risk_score,
            'weighted_risk_score': weighted_risk_score
        }), 200

    except Exception as e:
        logger.error(f"API check error: {str(e)}")
        log_api_call('/api/check', 'POST', 500)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/check-batch', methods=['POST'])
@limiter.limit("5 per minute")
def api_check_batch():
    """API endpoint to check multiple usernames"""
    data = request.get_json()
    usernames = data.get('usernames', [])

    if not usernames or not isinstance(usernames, list):
        log_api_call('/api/check-batch', 'POST', 400)
        return jsonify({'error': 'List of usernames required'}), 400

    if len(usernames) > 100:  # Limit batch size
        log_api_call('/api/check-batch', 'POST', 400)
        return jsonify({'error': 'Maximum 100 usernames per batch'}), 400

    try:
        batch_results = check_usernames_batch(usernames)

        # Save scans if authenticated
        if current_user.is_authenticated:
            for result in batch_results:
                if result['status'] == 'completed':
                    scan = Scan(
                        username=result['username'],
                        results=result['results'],
                        risk_score=result['risk_score'],
                        weighted_risk_score=result['weighted_risk_score'],
                        platforms_found_count=result['risk_score'],
                        total_platforms_checked=len(result['results']),
                        user_id=current_user.id
                    )
                    db.session.add(scan)
            db.session.commit()

        log_api_call('/api/check-batch', 'POST', 200)
        return jsonify({'results': batch_results}), 200

    except Exception as e:
        logger.error(f"API batch check error: {str(e)}")
        log_api_call('/api/check-batch', 'POST', 500)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    """Get user's search history"""
    try:
        history = SearchHistory.query.filter_by(user_id=current_user.id).order_by(
            SearchHistory.created_at.desc()
        ).limit(50).all()

        log_api_call('/api/history', 'GET', 200)
        return jsonify({
            'history': [h.to_dict() for h in history]
        }), 200

    except Exception as e:
        logger.error(f"API history error: {str(e)}")
        log_api_call('/api/history', 'GET', 500)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/results/<int:scan_id>', methods=['GET'])
def api_results(scan_id):
    """Get specific scan results"""
    try:
        scan = Scan.query.get(scan_id)

        if not scan:
            log_api_call(f'/api/results/{scan_id}', 'GET', 404)
            return jsonify({'error': 'Scan not found'}), 404

        # Check if user has permission to view
        if scan.user_id and scan.user_id != current_user.id:
            log_api_call(f'/api/results/{scan_id}', 'GET', 403)
            return jsonify({'error': 'Forbidden'}), 403

        log_api_call(f'/api/results/{scan_id}', 'GET', 200)
        return jsonify(scan.to_dict()), 200

    except Exception as e:
        logger.error(f"API results error: {str(e)}")
        log_api_call(f'/api/results/{scan_id}', 'GET', 500)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with statistics and history"""
    try:
        # Get user's scans
        scans = Scan.query.filter_by(user_id=current_user.id).order_by(
            Scan.created_at.desc()
        ).all()

        # Get search history
        history = SearchHistory.query.filter_by(user_id=current_user.id).order_by(
            SearchHistory.created_at.desc()
        ).limit(20).all()

        # Calculate statistics
        total_scans = len(scans)
        avg_risk_score = int(sum(s.risk_score for s in scans) / total_scans) if scans else 0

        # Find most found platform
        platform_counts = {}
        for scan in scans:
            for platform, result in scan.results.items():
                if result.get('found'):
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1

        most_found_platform = max(platform_counts, key=platform_counts.get) if platform_counts else 'N/A'

        return render_template(
            'dashboard.html',
            total_scans=total_scans,
            avg_risk_score=avg_risk_score,
            most_found_platform=most_found_platform,
            recent_scans=scans[:5],
            search_history=history
        )
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return redirect(url_for('index'))


@app.route('/scan/<int:scan_id>')
@login_required
def scan_detail(scan_id):
    """View detailed scan results"""
    try:
        scan = Scan.query.get(scan_id)

        if not scan or scan.user_id != current_user.id:
            return redirect(url_for('dashboard'))

        return render_template('scan_detail.html', scan=scan)
    except Exception as e:
        logger.error(f"Scan detail error: {str(e)}")
        return redirect(url_for('dashboard'))


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors"""
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)