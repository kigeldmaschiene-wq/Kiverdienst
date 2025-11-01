# -*- coding: utf-8 -*-
"""Setup API Routes"""
from fastapi import APIRouter
from app.database import get_pool

router = APIRouter()

@router.get("/status/")
async def get_setup_status():
    """Check if system is set up"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM brands")
        return {
            "setup_complete": count > 0,
            "brands_count": count
        }

@router.post("/complete/")
async def complete_setup():
    """Mark setup as complete"""
    return {"success": True, "message": "Setup completed"}
