#!/bin/bash

# KIVerdienst V2 - Phase 2 Quick Install Script
# Erstellt: 2025-10-31

echo "🚀 KIVerdienst V2 - Phase 2 Installation"
echo "========================================"
echo ""

# Check if webui exists
if [ ! -d "webui" ]; then
    echo "❌ Error: webui/ directory not found!"
    echo "   Please extract webui_phase2_complete.tar.gz first"
    exit 1
fi

cd webui

# Check Python
echo "📦 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "📚 Installing requirements..."
pip install --upgrade pip
pip install flask gunicorn requests

# Create database
echo "💾 Creating database..."
python3 << 'PYTHON'
import sqlite3
import os

db_path = 'kiverdienst.db'
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        niche TEXT,
        description TEXT,
        videos_per_day INTEGER DEFAULT 2,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        character_type TEXT,
        voice_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (brand_id) REFERENCES brands(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER,
        character_id INTEGER,
        title TEXT NOT NULL,
        platform TEXT,
        status TEXT DEFAULT 'draft',
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (brand_id) REFERENCES brands(id),
        FOREIGN KEY (character_id) REFERENCES characters(id)
    )''')
    
    conn.commit()
    conn.close()
    print("✅ Database created successfully!")
else:
    print("✅ Database already exists")
PYTHON

# Test server
echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Start the server with:"
echo "   cd webui"
echo "   source venv/bin/activate"
echo "   python3 app.py"
echo ""
echo "📍 Then visit:"
echo "   http://localhost:5000/dashboard"
echo ""
