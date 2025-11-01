# -*- coding: utf-8 -*-
"""Dashboard API Routes - MISSING ROUTE #1"""
from fastapi import APIRouter
from app.database import get_pool

router = APIRouter()

@router.get("/stats/")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Count brands
        brands_count = await conn.fetchval("SELECT COUNT(*) FROM brands WHERE active = TRUE")
        
        # Count videos
        videos_count = await conn.fetchval("SELECT COUNT(*) FROM videos")
        
        # Sum views
        total_views = await conn.fetchval("SELECT COALESCE(SUM(views), 0) FROM videos")
        
        # Calculate revenue (placeholder)
        total_revenue = await conn.fetchval("""
            SELECT COALESCE(SUM(price * sales_count * commission_percent / 100), 0)
            FROM products
        """)
        
        return {
            "brands": int(brands_count),
            "videos": int(videos_count),
            "views": int(total_views),
            "revenue": float(total_revenue)
        }
