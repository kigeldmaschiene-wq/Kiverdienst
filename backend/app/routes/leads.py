from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class LeadCreate(BaseModel):
    email: str
    name: Optional[str] = None
    brand_id: Optional[int] = None
    source: Optional[str] = None

@router.get("")
async def get_leads(brand_id: Optional[int] = None):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            if brand_id:
                rows = await conn.fetch(
                    "SELECT * FROM leads WHERE brand_id = $1 ORDER BY created_at DESC",
                    brand_id
                )
            else:
                rows = await conn.fetch("SELECT * FROM leads ORDER BY created_at DESC")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_lead(lead: LeadCreate):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            lead_id = await conn.fetchval(
                """INSERT INTO leads (email, name, brand_id, source, opt_in_date) 
                   VALUES ($1, $2, $3, $4, NOW()) RETURNING id""",
                lead.email, lead.name, lead.brand_id, lead.source
            )
        logger.info(f"Lead created: {lead_id}")
        return {"id": lead_id, "success": True}
    except Exception as e:
        logger.error(f"Failed to create lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))
