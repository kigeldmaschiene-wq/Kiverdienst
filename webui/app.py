# -*- coding: utf-8 -*-
"""
KIVerdienst V2 - Flask WebUI
Complete implementation with all API routes
"""

import sqlite3
import json
import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # UTF-8 in JSON
app.config['UPLOAD_FOLDER'] = '/opt/kiverdienst/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Database Helper
def get_db():
    conn = sqlite3.connect('/opt/kiverdienst/database/kiverdienst.db')
    conn.row_factory = sqlite3.Row
    return conn

# Error Handler
@app.errorhandler(Exception)
def handle_error(e):
    app.logger.error(f"Error: {str(e)}")
    return jsonify({'error': str(e)}), 500

# === PAGES (Templates) ===

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/brands')
def brands_page():
    return render_template('brands.html')

@app.route('/characters')
def characters_page():
    return render_template('characters.html')

@app.route('/videos')
def videos_page():
    return render_template('videos.html')

@app.route('/accounts')
def accounts_page():
    return render_template('accounts.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/products')
def products_page():
    return render_template('products.html')

@app.route('/leads')
def leads_page():
    return render_template('leads.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/logs')
def logs_page():
    return render_template('logs.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/landingpages')
def landingpages_page():
    return render_template('landingpages.html')

@app.route('/calendar')
def calendar_page():
    return render_template('calendar.html')

# === API: DASHBOARD ===

@app.route('/api/dashboard/stats', methods=['GET'])
def api_dashboard_stats():
    try:
        conn = get_db()
        
        # Brands count
        brands_count = conn.execute('SELECT COUNT(*) FROM brands WHERE active = 1').fetchone()[0]
        
        # Videos count
        videos_count = conn.execute('SELECT COUNT(*) FROM videos').fetchone()[0]
        
        # Total views
        total_views = conn.execute('SELECT SUM(views) FROM videos').fetchone()[0] or 0
        
        # Revenue (last 30 days)
        revenue = conn.execute('''
            SELECT SUM(commission_earned) FROM product_sales 
            WHERE sale_date >= date('now', '-30 days')
        ''').fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'brands_count': brands_count,
            'videos_count': videos_count,
            'total_views': total_views,
            'revenue': float(revenue)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === API: BRANDS ===

@app.route('/api/brands', methods=['GET'])
def api_get_brands():
    try:
        conn = get_db()
        brands = conn.execute('''
            SELECT b.*, 
                   COUNT(DISTINCT c.id) as character_count,
                   COUNT(DISTINCT v.id) as video_count
            FROM brands b
            LEFT JOIN characters c ON c.brand_id = b.id
            LEFT JOIN videos v ON v.brand_id = b.id
            GROUP BY b.id
            ORDER BY b.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(row) for row in brands]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/brands', methods=['POST'])
def api_create_brand():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO brands (name, niche, description, active, videos_per_day, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data.get('name'), data.get('niche'), data.get('description'), 
              data.get('active', 1), data.get('videos_per_day', 7), datetime.now()))
        conn.commit()
        brand_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': brand_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/brands/<int:id>', methods=['GET'])
def api_get_brand(id):
    try:
        conn = get_db()
        brand = conn.execute('SELECT * FROM brands WHERE id = ?', (id,)).fetchone()
        conn.close()
        if brand:
            return jsonify(dict(brand)), 200
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/brands/<int:id>', methods=['PUT'])
def api_update_brand(id):
    try:
        data = request.json
        conn = get_db()
        conn.execute('''
            UPDATE brands 
            SET name=?, niche=?, description=?, active=?, videos_per_day=?
            WHERE id=?
        ''', (data.get('name'), data.get('niche'), data.get('description'),
              data.get('active'), data.get('videos_per_day'), id))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/brands/<int:id>', methods=['DELETE'])
def api_delete_brand(id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM brands WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === API: CHARACTERS ===

@app.route('/api/characters', methods=['GET'])
def api_get_characters():
    try:
        conn = get_db()
        brand_id = request.args.get('brand_id')
        if brand_id:
            characters = conn.execute('''
                SELECT c.*, b.name as brand_name
                FROM characters c
                LEFT JOIN brands b ON b.id = c.brand_id
                WHERE c.brand_id = ?
                ORDER BY c.created_at DESC
            ''', (brand_id,)).fetchall()
        else:
            characters = conn.execute('''
                SELECT c.*, b.name as brand_name
                FROM characters c
                LEFT JOIN brands b ON b.id = c.brand_id
                ORDER BY c.created_at DESC
            ''').fetchall()
        conn.close()
        return jsonify([dict(row) for row in characters]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/characters', methods=['POST'])
def api_create_character():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO characters (name, brand_id, gender, character_type, voice_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data.get('name'), data.get('brand_id'), data.get('gender'), 
              data.get('character_type'), data.get('voice_id'), datetime.now()))
        conn.commit()
        character_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': character_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/characters/<int:id>', methods=['PUT'])
def api_update_character(id):
    try:
        data = request.json
        conn = get_db()
        conn.execute('''
            UPDATE characters 
            SET name=?, gender=?, character_type=?, voice_id=?
            WHERE id=?
        ''', (data.get('name'), data.get('gender'), data.get('character_type'),
              data.get('voice_id'), id))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/characters/<int:id>', methods=['DELETE'])
def api_delete_character(id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM characters WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === API: VIDEOS ===

@app.route('/api/videos', methods=['GET'])
def api_get_videos():
    try:
        conn = get_db()
        status = request.args.get('status')
        brand_id = request.args.get('brand_id')
        
        query = '''
            SELECT v.*, b.name as brand_name, c.name as character_name
            FROM videos v
            LEFT JOIN brands b ON b.id = v.brand_id
            LEFT JOIN characters c ON c.id = v.character_id
            WHERE 1=1
        '''
        params = []
        
        if status:
            query += ' AND v.status = ?'
            params.append(status)
        if brand_id:
            query += ' AND v.brand_id = ?'
            params.append(brand_id)
        
        query += ' ORDER BY v.created_at DESC LIMIT 100'
        
        videos = conn.execute(query, params).fetchall()
        conn.close()
        return jsonify([dict(row) for row in videos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos', methods=['POST'])
def api_create_video():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO videos (brand_id, character_id, title, script, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data.get('brand_id'), data.get('character_id'), data.get('title'),
              data.get('script'), data.get('status', 'draft'), datetime.now()))
        conn.commit()
        video_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': video_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<int:id>', methods=['DELETE'])
def api_delete_video(id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM videos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === API: PRODUCTS ===

@app.route('/api/products', methods=['GET'])
def api_get_products():
    try:
        conn = get_db()
        products = conn.execute('''
            SELECT p.*, COUNT(ps.id) as sales_count
            FROM products p
            LEFT JOIN product_sales ps ON ps.product_id = p.id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(row) for row in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def api_create_product():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, description, price, commission_rate, product_url, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data.get('name'), data.get('description'), data.get('price'),
              data.get('commission_rate'), data.get('product_url'), data.get('active', 1), datetime.now()))
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': product_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:id>', methods=['PUT'])
def api_update_product(id):
    try:
        data = request.json
        conn = get_db()
        conn.execute('''
            UPDATE products 
            SET name=?, description=?, price=?, commission_rate=?, product_url=?, active=?
            WHERE id=?
        ''', (data.get('name'), data.get('description'), data.get('price'),
              data.get('commission_rate'), data.get('product_url'), data.get('active'), id))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:id>', methods=['DELETE'])
def api_delete_product(id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === API: LEADS ===

@app.route('/api/leads', methods=['GET'])
def api_get_leads():
    try:
        conn = get_db()
        leads = conn.execute('''
            SELECT l.*, b.name as brand_name
            FROM leads l
            LEFT JOIN brands b ON b.id = l.brand_id
            ORDER BY l.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(row) for row in leads]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leads', methods=['POST'])
def api_create_lead():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leads (email, name, brand_id, source, status, subscribed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data.get('email'), data.get('name'), data.get('brand_id'),
              data.get('source'), data.get('status', 'active'), datetime.now()))
        conn.commit()
        lead_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': lead_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leads/<int:id>', methods=['DELETE'])
def api_delete_lead(id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM leads WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === API: ACCOUNTS ===

@app.route('/api/accounts', methods=['GET'])
def api_get_accounts():
    try:
        conn = get_db()
        accounts = conn.execute('''
            SELECT a.*, b.name as brand_name
            FROM accounts a
            LEFT JOIN brands b ON b.id = a.brand_id
            ORDER BY a.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(row) for row in accounts]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts', methods=['POST'])
def api_create_account():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO accounts (brand_id, platform, username, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.get('brand_id'), data.get('platform'), data.get('username'),
              data.get('status', 'active'), datetime.now()))
        conn.commit()
        account_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': account_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts/<int:id>', methods=['DELETE'])
def api_delete_account(id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM accounts WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === API: ANALYTICS ===

@app.route('/api/analytics/overview', methods=['GET'])
def api_analytics_overview():
    try:
        conn = get_db()
        
        # Top videos
        top_videos = conn.execute('''
            SELECT v.*, b.name as brand_name
            FROM videos v
            LEFT JOIN brands b ON b.id = v.brand_id
            WHERE v.views > 0
            ORDER BY v.views DESC
            LIMIT 5
        ''').fetchall()
        
        # Performance by brand
        brand_performance = conn.execute('''
            SELECT b.name, COUNT(v.id) as video_count, SUM(v.views) as total_views
            FROM brands b
            LEFT JOIN videos v ON v.brand_id = b.id
            GROUP BY b.id
            ORDER BY total_views DESC
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'top_videos': [dict(row) for row in top_videos],
            'brand_performance': [dict(row) for row in brand_performance]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === API: SETTINGS ===

@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    try:
        conn = get_db()
        settings = conn.execute('SELECT * FROM settings').fetchall()
        conn.close()
        return jsonify({row['setting_key']: row['setting_value'] for row in settings}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def api_update_settings():
    try:
        data = request.json
        conn = get_db()
        for key, value in data.items():
            conn.execute('''
                INSERT OR REPLACE INTO settings (setting_key, setting_value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, str(value), datetime.now()))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
