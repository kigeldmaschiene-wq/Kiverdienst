# -*- coding: utf-8 -*-
"""Brands API Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.database import get_pool

router = APIRouter()

class BrandCreate(BaseModel):
    name: str
    niche: Optional[str] = None
    description: Optional[str] = None
    videos_per_day: int = 2
    active: bool = True
    character_type: Optional[str] = None
    voice_id: Optional[str] = None
    platforms: Optional[dict] = {}
    schedule: Optional[dict] = {}

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    niche: Optional[str] = None
    description: Optional[str] = None
    videos_per_day: Optional[int] = None
    active: Optional[bool] = None
    character_type: Optional[str] = None
    voice_id: Optional[str] = None
    platforms: Optional[dict] = None
    schedule: Optional[dict] = None

@router.get("/")
async def list_brands():
    """List all brands"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT b.*, 
                   COUNT(DISTINCT c.id) as character_count,
                   COUNT(DISTINCT v.id) as video_count
            FROM brands b
            LEFT JOIN characters c ON c.brand_id = b.id
            LEFT JOIN videos v ON v.brand_id = b.id
            GROUP BY b.id
            ORDER BY b.created_at DESC
        """)
        return [dict(row) for row in rows]

@router.post("/")
async def create_brand(brand: BrandCreate):
    """Create new brand"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO brands (name, niche, description, videos_per_day, active, character_type, voice_id, platforms, schedule)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """, brand.name, brand.niche, brand.description, brand.videos_per_day, brand.active,
            brand.character_type, brand.voice_id, brand.platforms, brand.schedule)
        return dict(row)

@router.get("/{brand_id}/")
async def get_brand(brand_id: int):
    """Get single brand"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", brand_id)
        if not row:
            raise HTTPException(status_code=404, detail="Brand not found")
        return dict(row)

@router.put("/{brand_id}/")
async def update_brand(brand_id: int, brand: BrandUpdate):
    """Update brand"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Build dynamic update query
        updates = []
        values = []
        idx = 1
        for key, value in brand.dict(exclude_unset=True).items():
            updates.append(f"{key} = ${idx}")
            values.append(value)
            idx += 1
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(brand_id)
        query = f"UPDATE brands SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ${idx} RETURNING *"
        row = await conn.fetchrow(query, *values)
        
        if not row:
            raise HTTPException(status_code=404, detail="Brand not found")
        return dict(row)

@router.delete("/{brand_id}/")
async def delete_brand(brand_id: int):
    """Delete brand"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM brands WHERE id = $1", brand_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Brand not found")
        return {"success": True, "message": "Brand deleted"}
