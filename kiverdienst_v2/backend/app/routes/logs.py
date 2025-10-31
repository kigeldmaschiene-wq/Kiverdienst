# -*- coding: utf-8 -*-
"""System Logs API Routes - MISSING ROUTE #3"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from app.database import get_pool

router = APIRouter()

class LogEntry(BaseModel):
    level: str = "INFO"
    message: str
    details: Optional[str] = None

@router.get("/")
async def get_logs(
    level: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
):
    """Get system logs"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        if level and level != "all":
            rows = await conn.fetch("""
                SELECT * FROM system_logs 
                WHERE level = $1 
                ORDER BY timestamp DESC 
                LIMIT $2
            """, level, limit)
        else:
            rows = await conn.fetch("""
                SELECT * FROM system_logs 
                ORDER BY timestamp DESC 
                LIMIT $1
            """, limit)
        
        return [dict(row) for row in rows]

@router.post("/")
async def create_log(log: LogEntry):
    """Create log entry"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO system_logs (level, message, details)
            VALUES ($1, $2, $3)
            RETURNING *
        """, log.level, log.message, log.details)
        return dict(row)

@router.delete("/")
async def clear_logs():
    """Clear all logs"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM system_logs")
        # Add log entry about clearing
        await conn.execute("""
            INSERT INTO system_logs (level, message)
            VALUES ('INFO', 'All logs cleared')
        """)
        return {"success": True, "message": "Logs cleared"}
