# -*- coding: utf-8 -*-
"""Calendar API Routes - MISSING ROUTE #6"""
from fastapi import APIRouter, Query
from datetime import datetime, date
from app.database import get_pool

router = APIRouter()

@router.get("/")
async def get_calendar(
    month: int = Query(default=None),
    year: int = Query(default=None)
):
    """Get calendar data for a month"""
    if not month or not year:
        now = datetime.now()
        month = now.month
        year = now.year
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Get videos for the month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        rows = await conn.fetch("""
            SELECT 
                DATE(COALESCE(scheduled_at, created_at)) as date,
                v.id, v.title, v.platform, v.status, b.name as brand_name
            FROM videos v
            LEFT JOIN brands b ON b.id = v.brand_id
            WHERE DATE(COALESCE(scheduled_at, created_at)) >= $1 
              AND DATE(COALESCE(scheduled_at, created_at)) < $2
            ORDER BY date, v.created_at
        """, start_date, end_date)
        
        # Group by date
        calendar_data = {}
        for row in rows:
            date_str = str(row['date'])
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            calendar_data[date_str].append({
                "id": row['id'],
                "title": row['title'],
                "platform": row['platform'],
                "status": row['status'],
                "brand_name": row['brand_name']
            })
        
        return {
            "month": month,
            "year": year,
            "days": calendar_data
        }

@router.get("/day/{date_str}")
async def get_day_videos(date_str: str):
    """Get videos for a specific day"""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT v.*, b.name as brand_name
            FROM videos v
            LEFT JOIN brands b ON b.id = v.brand_id
            WHERE DATE(COALESCE(scheduled_at, created_at)) = $1
            ORDER BY v.created_at
        """, target_date)
        
        return [dict(row) for row in rows]
