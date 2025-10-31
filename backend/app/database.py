import asyncpg
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
pool = None

async def init_db():
    """Initialize database connection pool and schema"""
    global pool
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    logger.info("Creating database connection pool...")
    pool = await asyncpg.create_pool(
        database_url,
        min_size=2,
        max_size=10,
        command_timeout=60
    )
    
    logger.info("Initializing database schema...")
    async with pool.acquire() as conn:
        schema_path = Path("/app/database/schema.sql")
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            await conn.execute(schema_sql)
            logger.info("Database schema created from schema.sql")
        else:
            logger.warning("schema.sql not found, creating minimal schema")
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS setup_status (
                    id SERIAL PRIMARY KEY,
                    setup_complete BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                INSERT INTO setup_status (setup_complete) VALUES (false) 
                ON CONFLICT DO NOTHING;
            ''')
    
    logger.info("Database initialization complete")

async def get_pool():
    """Get database connection pool"""
    if pool is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return pool

async def close_pool():
    """Close database connection pool"""
    global pool
    if pool:
        await pool.close()
        pool = None
