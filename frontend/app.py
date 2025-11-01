from flask import Flask, render_template, request, jsonify
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

@app.route('/')
def index():
    """Main entry point - redirect to setup or dashboard"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/setup/status", timeout=5)
        if response.ok and response.json().get("setup_complete"):
            return render_template('dashboard.html')
    except Exception as e:
        logger.warning(f"Backend check failed: {e}")
    
    return render_template('setup.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/brands')
def brands():
    """Brand management"""
    return render_template('brands.html')

@app.route('/characters')
def characters():
    """Character library"""
    return render_template('characters.html')

@app.route('/videos')
def videos():
    """Video management"""
    return render_template('videos.html')

@app.route('/accounts')
def accounts():
    """Social media accounts"""
    return render_template('accounts.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    return render_template('analytics.html')

@app.route('/products')
def products():
    """Product management"""
    return render_template('products.html')

@app.route('/leads')
def leads():
    """Lead management"""
    return render_template('leads.html')

@app.route('/settings')
def settings():
    """System settings"""
    return render_template('settings.html')

@app.route('/logs')
def logs():
    """System logs"""
    return render_template('logs.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('dashboard.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
