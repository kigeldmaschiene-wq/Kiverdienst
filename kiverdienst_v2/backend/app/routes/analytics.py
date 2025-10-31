# -*- coding: utf-8 -*-
"""Analytics API Routes"""
from fastapi import APIRouter
from app.database import get_pool

router = APIRouter()

@router.get("/overview/")
async def get_analytics_overview():
    """Get analytics overview"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Get top videos
        top_videos = await conn.fetch("""
            SELECT v.*, b.name as brand_name
            FROM videos v
            LEFT JOIN brands b ON b.id = v.brand_id
            WHERE v.status = 'approved'
            ORDER BY v.views DESC
            LIMIT 10
        """)
        
        # Get brand performance
        brand_performance = await conn.fetch("""
            SELECT b.id as brand_id, b.name as brand_name,
                   COUNT(v.id) as video_count,
                   COALESCE(SUM(v.views), 0) as total_views,
                   COALESCE(SUM(v.likes), 0) as total_likes,
                   COALESCE(SUM(v.comments), 0) as total_comments
            FROM brands b
            LEFT JOIN videos v ON v.brand_id = b.id
            GROUP BY b.id, b.name
            ORDER BY total_views DESC
        """)
        
        # Get overall stats
        stats = await conn.fetchrow("""
            SELECT 
                COALESCE(SUM(views), 0) as total_views,
                COUNT(*) as total_videos,
                CASE 
                    WHEN SUM(views) > 0 THEN (SUM(likes) + SUM(comments))::float / SUM(views)
                    ELSE 0
                END as engagement_rate,
                0 as total_revenue
            FROM videos
        """)
        
        return {
            "top_videos": [dict(row) for row in top_videos],
            "brand_performance": [dict(row) for row in brand_performance],
            "total_views": int(stats['total_views']),
            "total_videos": stats['total_videos'],
            "engagement_rate": float(stats['engagement_rate']),
            "total_revenue": float(stats['total_revenue'])
        }
