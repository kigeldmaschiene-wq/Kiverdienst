from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class LeadCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    brand_id: Optional[int] = None
    source: Optional[str] = None
    status: str = "active"

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

@router.get("/")
async def list_leads():
    """Get all leads"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            leads = await conn.fetch("""
                SELECT l.*, b.name as brand_name
                FROM leads l
                LEFT JOIN brands b ON b.id = l.brand_id
                ORDER BY l.created_at DESC
            """)
            
            return [dict(lead) for lead in leads]
    
    except Exception as e:
        logger.error(f"Error fetching leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_lead(lead: LeadCreate):
    """Add new lead"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO leads (
                    email, name, brand_id, source, status, subscribed_at
                ) VALUES ($1, $2, $3, $4, $5, NOW())
                RETURNING *
            """, lead.email, lead.name, lead.brand_id, lead.source, lead.status)
            
            logger.info(f"Created lead: {lead.email}")
            return dict(result)
    
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{lead_id}")
async def update_lead(lead_id: int, lead: LeadUpdate):
    """Update lead"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            updates = []
            values = []
            idx = 1
            
            for field, value in lead.dict(exclude_unset=True).items():
                updates.append(f"{field} = ${idx}")
                values.append(value)
                idx += 1
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(lead_id)
            query = f"UPDATE leads SET {', '.join(updates)} WHERE id = ${idx} RETURNING *"
            
            result = await conn.fetchrow(query, *values)
            
            if not result:
                raise HTTPException(status_code=404, detail="Lead not found")
            
            logger.info(f"Updated lead: {lead_id}")
            return dict(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{lead_id}")
async def delete_lead(lead_id: int):
    """Delete lead"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM leads WHERE id = $1",
                lead_id
            )
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Lead not found")
            
            logger.info(f"Deleted lead: {lead_id}")
            return {"success": True, "message": "Lead deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sequences")
async def list_sequences():
    """Get email sequences"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            sequences = await conn.fetch("""
                SELECT s.*, b.name as brand_name,
                       COUNT(DISTINCT et.id) as email_count
                FROM email_sequences s
                LEFT JOIN brands b ON b.id = s.brand_id
                LEFT JOIN email_templates et ON et.sequence_id = s.id
                GROUP BY s.id, b.name
                ORDER BY s.created_at DESC
            """)
            
            return [dict(seq) for seq in sequences]
    
    except Exception as e:
        logger.error(f"Error fetching sequences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_lead_stats():
    """Get lead statistics"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            total_leads = await conn.fetchval("SELECT COUNT(*) FROM leads WHERE status = 'active'")
            
            total_sent = await conn.fetchval("SELECT COUNT(*) FROM email_sends WHERE sent_at IS NOT NULL")
            
            open_rate = await conn.fetchval("""
                SELECT COALESCE(AVG(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END), 0) * 100
                FROM email_sends WHERE sent_at IS NOT NULL
            """)
            
            click_rate = await conn.fetchval("""
                SELECT COALESCE(AVG(CASE WHEN clicked_at IS NOT NULL THEN 1 ELSE 0 END), 0) * 100
                FROM email_sends WHERE sent_at IS NOT NULL
            """)
            
            return {
                "total_leads": total_leads,
                "total_sent": total_sent,
                "open_rate": float(open_rate) if open_rate else 0.0,
                "click_rate": float(click_rate) if click_rate else 0.0
            }
    
    except Exception as e:
        logger.error(f"Error fetching lead stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
