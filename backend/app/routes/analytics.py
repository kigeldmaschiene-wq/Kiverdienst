from fastapi import APIRouter, HTTPException
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview")
async def get_analytics_overview():
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            brands_count = await conn.fetchval("SELECT COUNT(*) FROM brands")
            videos_count = await conn.fetchval("SELECT COUNT(*) FROM videos")
            total_views = await conn.fetchval(
                "SELECT COALESCE(SUM(views), 0) FROM videos"
            )
            total_revenue = await conn.fetchval(
                "SELECT COALESCE(SUM(amount), 0) FROM transactions"
            )
            
            return {
                "brands": brands_count or 0,
                "videos": videos_count or 0,
                "total_views": int(total_views) if total_views else 0,
                "revenue": float(total_revenue) if total_revenue else 0
            }
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}")
async def get_brand_analytics(brand_id: int):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            videos = await conn.fetchval(
                "SELECT COUNT(*) FROM videos WHERE brand_id = $1", brand_id
            )
            views = await conn.fetchval(
                "SELECT COALESCE(SUM(views), 0) FROM videos WHERE brand_id = $1",
                brand_id
            )
            revenue = await conn.fetchval(
                "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE brand_id = $1",
                brand_id
            )
            
            return {
                "videos": videos or 0,
                "views": int(views) if views else 0,
                "revenue": float(revenue) if revenue else 0
            }
    except Exception as e:
        logger.error(f"Failed to get brand analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
