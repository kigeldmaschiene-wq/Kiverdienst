from flask import Flask, render_template, jsonify
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
BACKEND = os.getenv("BACKEND_URL", "http://backend:8000")

def check_backend():
    """Check if backend is accessible"""
    try:
        r = requests.get(f"{BACKEND}/api/health", timeout=5)
        return r.status_code == 200
    except:
        return False

@app.route('/')
def index():
    """Main entry point - redirect to setup or dashboard"""
    try:
        r = requests.get(f"{BACKEND}/api/setup/status", timeout=5)
        if r.json().get("setup_complete"):
            return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Failed to check setup status: {e}")
    return render_template('setup.html')

@app.route('/setup')
def setup():
    return render_template('setup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/brands')
def brands():
    return render_template('brands.html')

@app.route('/characters')
def characters():
    return render_template('characters.html')

@app.route('/videos')
def videos():
    return render_template('videos.html')

@app.route('/accounts')
def accounts():
    return render_template('accounts.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/leads')
def leads():
    return render_template('leads.html')

@app.route('/content_strategy')
def content_strategy():
    return render_template('content_strategy.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/health')
def health():
    backend_ok = check_backend()
    return jsonify({
        "status": "healthy" if backend_ok else "degraded",
        "frontend": "running",
        "backend": "connected" if backend_ok else "disconnected"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
