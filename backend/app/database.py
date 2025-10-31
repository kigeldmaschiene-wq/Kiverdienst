import asyncpg
import os
import logging

logger = logging.getLogger(__name__)
pool = None

async def init_db():
    global pool
    database_url = os.getenv("DATABASE_URL")
    
    logger.info(f"Connecting to database...")
    pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
    
    # Read and execute schema.sql
    schema_path = "/app/database/schema.sql"
    if os.path.exists(schema_path):
        logger.info("Loading database schema...")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        async with pool.acquire() as conn:
            await conn.execute(schema_sql)
        logger.info("Database schema created successfully")
    else:
        logger.warning(f"Schema file not found at {schema_path}")
    
    logger.info("Database initialized successfully")

async def get_pool():
    if pool is None:
        raise RuntimeError("Database not initialized")
    return pool

async def close_db():
    global pool
    if pool:
        await pool.close()
        logger.info("Database connection closed")
