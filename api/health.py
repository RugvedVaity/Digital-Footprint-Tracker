from flask import request, jsonify
from app import app

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint for Vercel"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/scan-status', methods=['GET'])
def scan_status():
    """Check if scanning API is working"""
    return jsonify({'status': 'ready', 'message': 'Scanning API is operational'}), 200
