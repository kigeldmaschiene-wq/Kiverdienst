from fastapi import APIRouter, HTTPException
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/status")
async def get_status():
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT setup_complete FROM setup_status LIMIT 1"
            )
            return {"setup_complete": row['setup_complete'] if row else False}
    except Exception as e:
        logger.error(f"Failed to get setup status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/init")
async def init_setup():
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE setup_status SET setup_complete = true, last_step = 'completed'"
            )
        logger.info("Setup initialized successfully")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to initialize setup: {e}")
        raise HTTPException(status_code=500, detail=str(e))
