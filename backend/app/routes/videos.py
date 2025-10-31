from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class VideoCreate(BaseModel):
    brand_id: int
    title: str
    script: Optional[str] = None
    platform: Optional[str] = None

@router.get("")
async def get_videos(limit: int = 50, brand_id: Optional[int] = None):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            if brand_id:
                rows = await conn.fetch(
                    "SELECT * FROM videos WHERE brand_id = $1 ORDER BY created_at DESC LIMIT $2",
                    brand_id, limit
                )
            else:
                rows = await conn.fetch(
                    "SELECT * FROM videos ORDER BY created_at DESC LIMIT $1", limit
                )
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}")
async def get_video(video_id: int):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM videos WHERE id = $1", video_id
            )
            if not row:
                raise HTTPException(status_code=404, detail="Video not found")
            return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_video(video: VideoCreate):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            video_id = await conn.fetchval(
                """INSERT INTO videos (brand_id, title, script, platform, status) 
                   VALUES ($1, $2, $3, $4, 'draft') RETURNING id""",
                video.brand_id, video.title, video.script, video.platform
            )
        logger.info(f"Video created: {video_id}")
        return {"id": video_id, "success": True}
    except Exception as e:
        logger.error(f"Failed to create video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{video_id}")
async def delete_video(video_id: int):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM videos WHERE id = $1", video_id)
        logger.info(f"Video deleted: {video_id}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to delete video {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
