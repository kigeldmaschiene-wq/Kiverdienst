from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class BrandCreate(BaseModel):
    name: str
    niche: Optional[str] = None
    description: Optional[str] = None
    active: bool = True
    tiktok_enabled: bool = False
    tiktok_username: Optional[str] = None
    instagram_enabled: bool = False
    instagram_username: Optional[str] = None
    youtube_enabled: bool = False
    youtube_username: Optional[str] = None
    videos_per_day: int = 7
    posting_times: Optional[str] = None
    posting_days: Optional[str] = None

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    niche: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    tiktok_enabled: Optional[bool] = None
    tiktok_username: Optional[str] = None
    instagram_enabled: Optional[bool] = None
    instagram_username: Optional[str] = None
    youtube_enabled: Optional[bool] = None
    youtube_username: Optional[str] = None
    videos_per_day: Optional[int] = None
    posting_times: Optional[str] = None
    posting_days: Optional[str] = None

@router.get("/")
async def list_brands():
    """Get all brands"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            brands = await conn.fetch("""
                SELECT b.*, 
                       COUNT(DISTINCT c.id) as character_count,
                       COUNT(DISTINCT v.id) as video_count
                FROM brands b
                LEFT JOIN characters c ON c.brand_id = b.id
                LEFT JOIN videos v ON v.brand_id = b.id
                GROUP BY b.id
                ORDER BY b.created_at DESC
            """)
            
            return [dict(brand) for brand in brands]
    
    except Exception as e:
        logger.error(f"Error fetching brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{brand_id}")
async def get_brand(brand_id: int):
    """Get brand by ID"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            brand = await conn.fetchrow(
                "SELECT * FROM brands WHERE id = $1",
                brand_id
            )
            
            if not brand:
                raise HTTPException(status_code=404, detail="Brand not found")
            
            return dict(brand)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_brand(brand: BrandCreate):
    """Create new brand"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO brands (
                    name, niche, description, active, tiktok_enabled, tiktok_username,
                    instagram_enabled, instagram_username, youtube_enabled, youtube_username,
                    videos_per_day, posting_times, posting_days
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING *
            """, brand.name, brand.niche, brand.description, brand.active,
                brand.tiktok_enabled, brand.tiktok_username, brand.instagram_enabled,
                brand.instagram_username, brand.youtube_enabled, brand.youtube_username,
                brand.videos_per_day, brand.posting_times, brand.posting_days
            )
            
            logger.info(f"Created brand: {brand.name}")
            return dict(result)
    
    except Exception as e:
        logger.error(f"Error creating brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{brand_id}")
async def update_brand(brand_id: int, brand: BrandUpdate):
    """Update brand"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Build dynamic update query
            updates = []
            values = []
            idx = 1
            
            for field, value in brand.dict(exclude_unset=True).items():
                updates.append(f"{field} = ${idx}")
                values.append(value)
                idx += 1
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(brand_id)
            query = f"UPDATE brands SET {', '.join(updates)} WHERE id = ${idx} RETURNING *"
            
            result = await conn.fetchrow(query, *values)
            
            if not result:
                raise HTTPException(status_code=404, detail="Brand not found")
            
            logger.info(f"Updated brand: {brand_id}")
            return dict(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{brand_id}")
async def delete_brand(brand_id: int):
    """Delete brand"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM brands WHERE id = $1",
                brand_id
            )
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Brand not found")
            
            logger.info(f"Deleted brand: {brand_id}")
            return {"success": True, "message": "Brand deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{brand_id}/toggle")
async def toggle_brand_active(brand_id: int):
    """Toggle brand active status"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                UPDATE brands 
                SET active = NOT active 
                WHERE id = $1 
                RETURNING *
            """, brand_id)
            
            if not result:
                raise HTTPException(status_code=404, detail="Brand not found")
            
            logger.info(f"Toggled brand {brand_id} active status to {result['active']}")
            return dict(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))
