# -*- coding: utf-8 -*-
"""
Content Generation API Routes
NEW ROUTES for AI-powered video generation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_pool
from app.agents.mastermind import MastermindAgent

router = APIRouter()

# Initialize agents
mastermind = MastermindAgent()

class VideoGenerateRequest(BaseModel):
    brand_id: int
    topic: str
    platform: str = "tiktok"

class BatchGenerateRequest(BaseModel):
    brand_id: int
    count: int = 10

@router.post("/generate/")
async def generate_video(request: VideoGenerateRequest):
    """
    Generate single video
    
    POST /api/content/generate/
    Body: {
        "brand_id": 1,
        "topic": "3 AI tools that save 5 hours",
        "platform": "tiktok"
    }
    
    Returns: {
        "success": true,
        "job_id": 123,
        "status": "queued"
    }
    """
    # Create queue entry
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            INSERT INTO generation_queue (brand_id, topic, platform, status, priority)
            VALUES ($1, $2, $3, 'queued', 0)
            RETURNING id
        """, request.brand_id, request.topic, request.platform)
        
        return {
            'success': True,
            'job_id': result['id'],
            'status': 'queued',
            'message': 'Video generation queued - worker will process it'
        }

@router.post("/generate/batch/")
async def generate_batch(request: BatchGenerateRequest):
    """
    Generate batch of videos for brand
    Uses Mastermind to select topics
    
    POST /api/content/generate/batch/
    Body: {
        "brand_id": 1,
        "count": 10
    }
    
    Returns: {
        "success": true,
        "jobs_created": 10,
        "job_ids": [1, 2, 3, ...]
    }
    """
    # Select topics with Mastermind
    result = await mastermind.execute(
        task="select_topics",
        context={
            'brand_id': request.brand_id,
            'count': request.count
        }
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Topic selection failed'))
    
    topics = result['data']['topics']
    
    # Create queue entries for all topics
    pool = await get_pool()
    job_ids = []
    
    async with pool.acquire() as conn:
        for topic in topics:
            job = await conn.fetchrow("""
                INSERT INTO generation_queue (brand_id, topic, platform, status)
                VALUES ($1, $2, 'tiktok', 'queued')
                RETURNING id
            """, request.brand_id, topic)
            job_ids.append(job['id'])
    
    return {
        'success': True,
        'jobs_created': len(job_ids),
        'job_ids': job_ids,
        'topics': topics
    }

@router.get("/status/{job_id}/")
async def get_status(job_id: int):
    """
    Get job status
    
    GET /api/content/status/123/
    
    Returns: {
        "id": 123,
        "status": "processing",
        "topic": "...",
        "video_id": 456
    }
    """
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        job = await conn.fetchrow("SELECT * FROM generation_queue WHERE id = $1", job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return dict(job)

@router.get("/queue/")
async def get_queue(status: Optional[str] = None):
    """
    Get all jobs in queue
    
    GET /api/content/queue/?status=queued
    
    Returns: [
        {"id": 1, "status": "queued", ...},
        ...
    ]
    """
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        if status:
            rows = await conn.fetch("""
                SELECT * FROM generation_queue
                WHERE status = $1
                ORDER BY priority DESC, created_at ASC
            """, status)
        else:
            rows = await conn.fetch("""
                SELECT * FROM generation_queue
                ORDER BY created_at DESC
                LIMIT 50
            """)
        
        return [dict(row) for row in rows]
