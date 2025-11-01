# -*- coding: utf-8 -*-
"""Content Generation Routes - Converted to FastAPI"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
from app.database import get_db
import psycopg2.extras

router = APIRouter()

# Import agents with asyncio wrapper
from app.agents.mastermind import MastermindAgent
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
    """Generate single video"""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute("""
        INSERT INTO generation_queue (brand_id, topic, platform, status)
        VALUES (%s, %s, %s, 'queued')
        RETURNING id
    """, (request.brand_id, request.topic, request.platform))
    
    job = cursor.fetchone()
    db.commit()
    cursor.close()
    
    return {'success': True, 'job_id': job['id'], 'status': 'queued'}

@router.post("/generate/batch/")
async def generate_batch(request: BatchGenerateRequest):
    """Generate batch with Mastermind topic selection"""
    # Run mastermind in thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: asyncio.run(mastermind.execute("select_topics", {
            'brand_id': request.brand_id,
            'count': request.count
        }))
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error'))
    
    topics = result['data']['topics']
    
    db = get_db()
    cursor = db.cursor()
    job_ids = []
    
    for topic in topics:
        cursor.execute("""
            INSERT INTO generation_queue (brand_id, topic, platform, status)
            VALUES (%s, %s, 'tiktok', 'queued')
            RETURNING id
        """, (request.brand_id, topic))
        job_ids.append(cursor.fetchone()[0])
    
    db.commit()
    cursor.close()
    
    return {'success': True, 'jobs_created': len(job_ids), 'job_ids': job_ids, 'topics': topics}

@router.get("/queue/")
async def get_queue(status: Optional[str] = None):
    """Get generation queue"""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    if status:
        cursor.execute("""
            SELECT * FROM generation_queue WHERE status = %s
            ORDER BY priority DESC, created_at ASC
        """, (status,))
    else:
        cursor.execute("""
            SELECT * FROM generation_queue
            ORDER BY created_at DESC LIMIT 50
        """)
    
    jobs = cursor.fetchall()
    cursor.close()
    
    return [dict(job) for job in jobs]

@router.get("/status/{job_id}/")
async def get_status(job_id: int):
    """Get job status"""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute("SELECT * FROM generation_queue WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    cursor.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return dict(job)
