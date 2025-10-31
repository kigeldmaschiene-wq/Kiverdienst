# -*- coding: utf-8 -*-
"""Landing Pages API Routes - MISSING ROUTE #5"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_pool

router = APIRouter()

class LandingPageCreate(BaseModel):
    title: str
    headline: Optional[str] = None
    description: Optional[str] = None
    lead_magnet_type: str = "PDF"
    button_text: str = "Jetzt kostenlos sichern"
    template: str = "modern"
    color_scheme: str = "blue"
    hero_image_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    keywords: Optional[str] = None

class LandingPageUpdate(BaseModel):
    title: Optional[str] = None
    headline: Optional[str] = None
    description: Optional[str] = None
    lead_magnet_type: Optional[str] = None
    button_text: Optional[str] = None
    template: Optional[str] = None
    color_scheme: Optional[str] = None
    hero_image_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    keywords: Optional[str] = None
    status: Optional[str] = None

@router.get("/")
async def list_landing_pages():
    """List all landing pages"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM landing_pages 
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in rows]

@router.post("/")
async def create_landing_page(page: LandingPageCreate):
    """Create new landing page"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO landing_pages (
                title, headline, description, lead_magnet_type, button_text,
                template, color_scheme, hero_image_url, meta_title, meta_description, keywords
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING *
        """, page.title, page.headline, page.description, page.lead_magnet_type, page.button_text,
            page.template, page.color_scheme, page.hero_image_url, page.meta_title, 
            page.meta_description, page.keywords)
        return dict(row)

@router.get("/{page_id}/")
async def get_landing_page(page_id: int):
    """Get single landing page"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM landing_pages WHERE id = $1", page_id)
        if not row:
            raise HTTPException(status_code=404, detail="Landing page not found")
        return dict(row)

@router.put("/{page_id}/")
async def update_landing_page(page_id: int, page: LandingPageUpdate):
    """Update landing page"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        updates = []
        values = []
        idx = 1
        for key, value in page.dict(exclude_unset=True).items():
            updates.append(f"{key} = ${idx}")
            values.append(value)
            idx += 1
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(page_id)
        query = f"UPDATE landing_pages SET {', '.join(updates)} WHERE id = ${idx} RETURNING *"
        row = await conn.fetchrow(query, *values)
        
        if not row:
            raise HTTPException(status_code=404, detail="Landing page not found")
        return dict(row)

@router.delete("/{page_id}/")
async def delete_landing_page(page_id: int):
    """Delete landing page"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM landing_pages WHERE id = $1", page_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Landing page not found")
        return {"success": True, "message": "Landing page deleted"}
