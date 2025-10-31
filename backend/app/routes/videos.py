from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class VideoGenerate(BaseModel):
    brand_id: int
    character_id: Optional[int] = None
    topic: Optional[str] = None
    platform: str = "tiktok"

@router.get("/")
async def list_videos(
    status: Optional[str] = Query(None),
    brand_id: Optional[int] = Query(None),
    platform: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """Get videos with optional filters"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            query = """
                SELECT v.*, b.name as brand_name, c.name as character_name
                FROM videos v
                LEFT JOIN brands b ON b.id = v.brand_id
                LEFT JOIN characters c ON c.id = v.character_id
                WHERE 1=1
            """
            params = []
            idx = 1
            
            if status:
                query += f" AND v.status = ${idx}"
                params.append(status)
                idx += 1
            
            if brand_id:
                query += f" AND v.brand_id = ${idx}"
                params.append(brand_id)
                idx += 1
            
            if platform:
                query += f" AND v.platform = ${idx}"
                params.append(platform)
                idx += 1
            
            query += f" ORDER BY v.created_at DESC LIMIT ${idx}"
            params.append(limit)
            
            videos = await conn.fetch(query, *params)
            
            return [dict(video) for video in videos]
    
    except Exception as e:
        logger.error(f"Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}")
async def get_video(video_id: int):
    """Get video by ID"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            video = await conn.fetchrow("""
                SELECT v.*, b.name as brand_name, c.name as character_name
                FROM videos v
                LEFT JOIN brands b ON b.id = v.brand_id
                LEFT JOIN characters c ON c.id = v.character_id
                WHERE v.id = $1
            """, video_id)
            
            if not video:
                raise HTTPException(status_code=404, detail="Video not found")
            
            return dict(video)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_video(request: VideoGenerate):
    """Trigger video generation"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Create video record
            video = await conn.fetchrow("""
                INSERT INTO videos (
                    brand_id, character_id, platform, status, title
                ) VALUES ($1, $2, $3, 'generating', $4)
                RETURNING *
            """, request.brand_id, request.character_id, request.platform,
                request.topic or "AI Generated Video"
            )
            
            # Create agent task for video generation
            await conn.execute("""
                INSERT INTO agent_tasks (agent_name, task_type, task_data, status)
                VALUES ('VideoWorker', 'generate_video', $1, 'pending')
            """, {
                "video_id": video['id'],
                "brand_id": request.brand_id,
                "character_id": request.character_id,
                "topic": request.topic
            })
            
            logger.info(f"Created video generation task: {video['id']}")
            return {
                "success": True,
                "video_id": video['id'],
                "status": "generating",
                "message": "Video generation started"
            }
    
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{video_id}")
async def delete_video(video_id: int):
    """Delete video"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM videos WHERE id = $1",
                video_id
            )
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Video not found")
            
            logger.info(f"Deleted video: {video_id}")
            return {"success": True, "message": "Video deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{video_id}/approve")
async def approve_video(video_id: int):
    """Approve video for posting"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            video = await conn.fetchrow("""
                UPDATE videos 
                SET status = 'approved'
                WHERE id = $1
                RETURNING *
            """, video_id)
            
            if not video:
                raise HTTPException(status_code=404, detail="Video not found")
            
            logger.info(f"Approved video: {video_id}")
            return dict(video)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}/performance")
async def get_video_performance(video_id: int):
    """Get video performance metrics"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            video = await conn.fetchrow(
                "SELECT * FROM videos WHERE id = $1",
                video_id
            )
            
            if not video:
                raise HTTPException(status_code=404, detail="Video not found")
            
            snapshots = await conn.fetch("""
                SELECT * FROM analytics_snapshots 
                WHERE video_id = $1 
                ORDER BY snapshot_date ASC
            """, video_id)
            
            return {
                "video": dict(video),
                "snapshots": [dict(s) for s in snapshots],
                "total_views": video['views'],
                "total_likes": video['likes'],
                "total_comments": video['comments'],
                "total_shares": video['shares'],
                "engagement_rate": video['engagement_rate']
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
