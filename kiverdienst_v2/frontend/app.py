# -*- coding: utf-8 -*-
"""
KIVerdienst V2 - Flask Frontend
Serves all HTML templates
"""
import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Page routes
@app.route('/')
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

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/landingpages')
def landingpages():
    return render_template('landingpages.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
