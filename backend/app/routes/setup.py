from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SetupRequest(BaseModel):
    admin_password: str = None

@router.get("/status")
async def get_setup_status():
    """Check if initial setup is complete"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT setup_complete, created_at FROM setup_status ORDER BY id DESC LIMIT 1"
            )
            
            if result:
                return {
                    "setup_complete": result['setup_complete'],
                    "created_at": result['created_at'].isoformat() if result['created_at'] else None
                }
            
            return {"setup_complete": False, "created_at": None}
    
    except Exception as e:
        logger.error(f"Error checking setup status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/init")
async def initialize_setup(request: SetupRequest = None):
    """Mark setup as complete and initialize default data"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Mark setup as complete
            await conn.execute(
                "UPDATE setup_status SET setup_complete = true WHERE id = (SELECT id FROM setup_status ORDER BY id DESC LIMIT 1)"
            )
            
            # Create default brands if none exist
            brand_count = await conn.fetchval("SELECT COUNT(*) FROM brands")
            if brand_count == 0:
                logger.info("Creating default brands...")
                await conn.execute("""
                    INSERT INTO brands (name, niche, description, active, videos_per_day) VALUES
                    ('KI Hustle', 'KI & Online Business', 'KI-Tools und Online-Verdienstm?glichkeiten', true, 7),
                    ('Sparfuchs', 'Finanzen & Sparen', 'Spartipps und Finanz-Hacks', true, 7),
                    ('Purr Paradise', 'Haustiere & Katzen', 'S??e Katzen-Momente', true, 7),
                    ('Oddly Bliss', 'ASMR & Entspannung', 'Beruhigende ASMR-Inhalte', true, 7)
                """)
            
            return {
                "success": True,
                "message": "Setup completed successfully",
                "brands_created": brand_count == 0
            }
    
    except Exception as e:
        logger.error(f"Setup initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_system_config():
    """Get system configuration"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            settings = await conn.fetch("SELECT setting_key, setting_value FROM settings")
            
            config = {}
            for row in settings:
                config[row['setting_key']] = row['setting_value']
            
            return {"config": config}
    
    except Exception as e:
        logger.error(f"Error fetching config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
