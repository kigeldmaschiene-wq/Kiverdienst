# -*- coding: utf-8 -*-
"""
Approval Queue API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_pool

router = APIRouter()

class ApproveRequest(BaseModel):
    approved_by: str = "user"

class RejectRequest(BaseModel):
    rejected_reason: str

@router.get("/queue/")
async def get_queue(status: str = "pending"):
    """
    Get approval queue
    
    GET /api/approval/queue/?status=pending
    """
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM approval_queue
            WHERE status = $1
            ORDER BY created_at DESC
        """, status)
        
        return [dict(row) for row in rows]

@router.post("/approve/{item_id}/")
async def approve_item(item_id: int, request: ApproveRequest):
    """Approve item"""
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE approval_queue
            SET status = 'approved', 
                approved_by = $1, 
                approved_at = NOW()
            WHERE id = $2
        """, request.approved_by, item_id)
        
        return {'success': True, 'message': 'Item approved'}

@router.post("/reject/{item_id}/")
async def reject_item(item_id: int, request: RejectRequest):
    """Reject item"""
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE approval_queue
            SET status = 'rejected', 
                rejected_reason = $1
            WHERE id = $2
        """, request.rejected_reason, item_id)
        
        return {'success': True, 'message': 'Item rejected'}
