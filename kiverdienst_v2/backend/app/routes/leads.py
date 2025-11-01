# -*- coding: utf-8 -*-
"""Leads API Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_pool

router = APIRouter()

class LeadCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    source: str
    brand_id: Optional[int] = None
    notes: Optional[str] = None

@router.get("/")
async def list_leads():
    """List all leads"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT l.*, b.name as brand_name
            FROM leads l
            LEFT JOIN brands b ON b.id = l.brand_id
            ORDER BY l.created_at DESC
        """)
        return [dict(row) for row in rows]

@router.post("/")
async def create_lead(lead: LeadCreate):
    """Create new lead"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
                INSERT INTO leads (email, name, source, brand_id, notes)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            """, lead.email, lead.name, lead.source, lead.brand_id, lead.notes)
            return dict(row)
        except Exception as e:
            if "unique" in str(e).lower():
                raise HTTPException(status_code=400, detail="Email already exists")
            raise

@router.delete("/{lead_id}/")
async def delete_lead(lead_id: int):
    """Delete lead"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM leads WHERE id = $1", lead_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Lead not found")
        return {"success": True, "message": "Lead deleted"}
