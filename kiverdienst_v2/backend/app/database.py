# -*- coding: utf-8 -*-
"""
KIVerdienst V2 - Database Management
Handles PostgreSQL connection pool and table initialization
"""
import os
import asyncpg
import logging

logger = logging.getLogger(__name__)

# Global connection pool
_pool = None

async def get_pool():
    """Get or create database connection pool"""
    global _pool
    if _pool is None:
        _pool = await create_pool()
    return _pool

async def create_pool():
    """Create new database connection pool"""
    return await asyncpg.create_pool(
        host=os.getenv('DB_HOST', 'postgres'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME', 'kiverdienst_v2'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'kiverdienst2024secure'),
        min_size=2,
        max_size=10
    )

async def close_pool():
    """Close database connection pool"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

async def init_db():
    """Initialize database tables"""
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # Create tables
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS brands (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                niche VARCHAR(100),
                description TEXT,
                videos_per_day INTEGER DEFAULT 2,
                active BOOLEAN DEFAULT TRUE,
                character_type VARCHAR(100),
                voice_id VARCHAR(255),
                platforms JSONB DEFAULT '[]'::jsonb,
                schedule JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id SERIAL PRIMARY KEY,
                brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                age INTEGER,
                gender VARCHAR(50),
                character_type VARCHAR(100),
                voice_id VARCHAR(255),
                reference_image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id SERIAL PRIMARY KEY,
                brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
                character_id INTEGER REFERENCES characters(id) ON DELETE SET NULL,
                title TEXT NOT NULL,
                platform VARCHAR(50),
                status VARCHAR(50) DEFAULT 'draft',
                character_percentage INTEGER DEFAULT 70,
                video_url TEXT,
                thumbnail_url TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_at TIMESTAMP,
                published_at TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2),
                commission_percent DECIMAL(5, 2),
                affiliate_link TEXT,
                niche VARCHAR(100),
                image_url TEXT,
                sales_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(255),
                source VARCHAR(255),
                brand_id INTEGER REFERENCES brands(id) ON DELETE SET NULL,
                status VARCHAR(50) DEFAULT 'new',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                platform VARCHAR(50) NOT NULL,
                brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
                username VARCHAR(255) NOT NULL,
                session_data TEXT,
                status VARCHAR(50) DEFAULT 'active',
                followers INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS analytics_data (
                id SERIAL PRIMARY KEY,
                brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
                video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                revenue DECIMAL(10, 2) DEFAULT 0,
                date DATE DEFAULT CURRENT_DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # NEW TABLES for missing routes
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key VARCHAR(255) PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                level VARCHAR(50) DEFAULT 'INFO',
                message TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                role VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS landing_pages (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                headline VARCHAR(500),
                description TEXT,
                lead_magnet_type VARCHAR(100),
                button_text VARCHAR(255),
                template VARCHAR(100),
                color_scheme VARCHAR(100),
                hero_image_url TEXT,
                meta_title VARCHAR(255),
                meta_description TEXT,
                keywords TEXT,
                status VARCHAR(50) DEFAULT 'active',
                views INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        logger.info("? All database tables created successfully")
        
        # Insert demo data if brands table is empty
        count = await conn.fetchval('SELECT COUNT(*) FROM brands')
        if count == 0:
            await conn.execute('''
                INSERT INTO brands (name, niche, description, videos_per_day, active)
                VALUES 
                    ('TechSnap', 'Technology', 'Tech news and gadget reviews', 3, TRUE),
                    ('FinanzFuchs', 'Finance', 'Personal finance tips and investment advice', 2, TRUE),
                    ('FitLife', 'Health & Fitness', 'Workout routines and nutrition tips', 4, TRUE),
                    ('TravelVibes', 'Travel', 'Travel destinations and tips', 2, TRUE)
            ''')
            logger.info("? Demo brands inserted")
            
            # Insert initial log entry
            await conn.execute('''
                INSERT INTO system_logs (level, message, details)
                VALUES ('INFO', 'System initialized', 'KIVerdienst V2 started successfully')
            ''')
            logger.info("? Initial system log created")
