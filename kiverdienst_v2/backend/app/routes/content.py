# -*- coding: utf-8 -*-
"""Content Generation API Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_pool

router = APIRouter()

class ContentGenerateRequest(BaseModel):
    brand_id: int
    topic: str
    platform: str = "tiktok"

@router.post("/generate/")
async def generate_content(request: ContentGenerateRequest):
    """Generate content (placeholder - will trigger AI agents)"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Get brand info
        brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", request.brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Create video entry
        video = await conn.fetchrow("""
            INSERT INTO videos (brand_id, title, platform, status)
            VALUES ($1, $2, $3, 'generating')
            RETURNING *
        """, request.brand_id, request.topic, request.platform)
        
        # Log the generation request
        await conn.execute("""
            INSERT INTO system_logs (level, message, details)
            VALUES ('INFO', 'Content generation started', $1)
        """, f"Brand: {brand['name']}, Topic: {request.topic}")
        
        return {
            "success": True,
            "video_id": video['id'],
            "message": "Content generation started",
            "status": "generating"
        }

@router.get("/status/{video_id}/")
async def get_generation_status(video_id: int):
    """Get content generation status"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        video = await conn.fetchrow("SELECT * FROM videos WHERE id = $1", video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return dict(video)
