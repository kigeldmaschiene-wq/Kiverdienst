# -*- coding: utf-8 -*-
"""Videos API Routes"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.database import get_pool

router = APIRouter()

class VideoCreate(BaseModel):
    brand_id: int
    title: str
    platform: str
    character_id: Optional[int] = None
    character_percentage: int = 70
    status: str = "draft"

@router.get("/")
async def list_videos(status: Optional[str] = None, brand_id: Optional[int] = None):
    """List all videos with optional filters"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        query = """
            SELECT v.*, b.name as brand_name
            FROM videos v
            LEFT JOIN brands b ON b.id = v.brand_id
            WHERE 1=1
        """
        params = []
        if status:
            params.append(status)
            query += f" AND v.status = ${len(params)}"
        if brand_id:
            params.append(brand_id)
            query += f" AND v.brand_id = ${len(params)}"
        query += " ORDER BY v.created_at DESC"
        
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

@router.post("/")
async def create_video(video: VideoCreate):
    """Create new video"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO videos (brand_id, title, platform, character_id, character_percentage, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """, video.brand_id, video.title, video.platform, video.character_id,
            video.character_percentage, video.status)
        return dict(row)

@router.delete("/{video_id}/")
async def delete_video(video_id: int):
    """Delete video"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM videos WHERE id = $1", video_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Video not found")
        return {"success": True, "message": "Video deleted"}
