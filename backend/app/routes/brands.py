from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class BrandCreate(BaseModel):
    name: str
    niche: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    niche: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    tiktok_enabled: Optional[bool] = None
    instagram_enabled: Optional[bool] = None
    youtube_enabled: Optional[bool] = None

@router.get("")
async def get_brands():
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM brands ORDER BY name")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{brand_id}")
async def get_brand(brand_id: int):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM brands WHERE id = $1", brand_id
            )
            if not row:
                raise HTTPException(status_code=404, detail="Brand not found")
            return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_brand(brand: BrandCreate):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            brand_id = await conn.fetchval(
                """INSERT INTO brands (name, niche, tagline, description) 
                   VALUES ($1, $2, $3, $4) RETURNING id""",
                brand.name, brand.niche, brand.tagline, brand.description
            )
        logger.info(f"Brand created: {brand_id}")
        return {"id": brand_id, "success": True}
    except Exception as e:
        logger.error(f"Failed to create brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{brand_id}")
async def update_brand(brand_id: int, brand: BrandUpdate):
    try:
        pool = await get_pool()
        updates = []
        values = []
        idx = 1
        
        if brand.name:
            updates.append(f"name = ${idx}")
            values.append(brand.name)
            idx += 1
        if brand.niche:
            updates.append(f"niche = ${idx}")
            values.append(brand.niche)
            idx += 1
        if brand.active is not None:
            updates.append(f"active = ${idx}")
            values.append(brand.active)
            idx += 1
        if brand.tiktok_enabled is not None:
            updates.append(f"tiktok_enabled = ${idx}")
            values.append(brand.tiktok_enabled)
            idx += 1
        
        if not updates:
            return {"success": True}
        
        query = f"UPDATE brands SET {', '.join(updates)} WHERE id = ${idx}"
        values.append(brand_id)
        
        async with pool.acquire() as conn:
            await conn.execute(query, *values)
        
        logger.info(f"Brand updated: {brand_id}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to update brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{brand_id}")
async def delete_brand(brand_id: int):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM brands WHERE id = $1", brand_id)
        logger.info(f"Brand deleted: {brand_id}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to delete brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
