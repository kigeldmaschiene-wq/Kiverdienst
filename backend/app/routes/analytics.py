from fastapi import APIRouter, HTTPException
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview")
async def get_overview():
    """Get system-wide analytics overview"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Count brands
            brands = await conn.fetchval("SELECT COUNT(*) FROM brands WHERE active = true")
            
            # Count videos
            videos = await conn.fetchval("SELECT COUNT(*) FROM videos")
            
            # Total views
            total_views = await conn.fetchval("SELECT COALESCE(SUM(views), 0) FROM videos")
            
            # Total revenue (from sales)
            revenue = await conn.fetchval("""
                SELECT COALESCE(SUM(commission_earned), 0) 
                FROM product_sales 
                WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days'
            """)
            
            # Recent videos
            recent_videos = await conn.fetch("""
                SELECT v.*, b.name as brand_name
                FROM videos v
                LEFT JOIN brands b ON b.id = v.brand_id
                ORDER BY v.created_at DESC
                LIMIT 10
            """)
            
            # Top performing videos
            top_videos = await conn.fetch("""
                SELECT v.*, b.name as brand_name
                FROM videos v
                LEFT JOIN brands b ON b.id = v.brand_id
                WHERE v.views > 0
                ORDER BY v.views DESC
                LIMIT 5
            """)
            
            return {
                "brands": brands,
                "videos": videos,
                "total_views": total_views,
                "revenue": float(revenue) if revenue else 0.0,
                "recent_videos": [dict(v) for v in recent_videos],
                "top_videos": [dict(v) for v in top_videos]
            }
    
    except Exception as e:
        logger.error(f"Error fetching overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}")
async def get_brand_analytics(brand_id: int):
    """Get analytics for specific brand"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Brand info
            brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", brand_id)
            if not brand:
                raise HTTPException(status_code=404, detail="Brand not found")
            
            # Video stats
            video_count = await conn.fetchval(
                "SELECT COUNT(*) FROM videos WHERE brand_id = $1", brand_id
            )
            
            total_views = await conn.fetchval(
                "SELECT COALESCE(SUM(views), 0) FROM videos WHERE brand_id = $1", brand_id
            )
            
            avg_engagement = await conn.fetchval(
                "SELECT COALESCE(AVG(engagement_rate), 0) FROM videos WHERE brand_id = $1 AND engagement_rate IS NOT NULL",
                brand_id
            )
            
            # Revenue
            brand_revenue = await conn.fetchval("""
                SELECT COALESCE(SUM(commission_earned), 0)
                FROM product_sales
                WHERE brand_id = $1 AND sale_date >= CURRENT_DATE - INTERVAL '30 days'
            """, brand_id)
            
            # Recent videos
            recent_videos = await conn.fetch("""
                SELECT * FROM videos 
                WHERE brand_id = $1 
                ORDER BY created_at DESC 
                LIMIT 10
            """, brand_id)
            
            return {
                "brand": dict(brand),
                "video_count": video_count,
                "total_views": total_views,
                "avg_engagement": float(avg_engagement) if avg_engagement else 0.0,
                "revenue": float(brand_revenue) if brand_revenue else 0.0,
                "recent_videos": [dict(v) for v in recent_videos]
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching brand analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_trending_topics():
    """Get trending topics"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            trends = await conn.fetch("""
                SELECT t.*, n.niche_name
                FROM trending_topics t
                LEFT JOIN niches n ON n.id = t.niche_id
                WHERE t.detected_at >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY t.trend_score DESC
                LIMIT 20
            """)
            
            return [dict(t) for t in trends]
    
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))
