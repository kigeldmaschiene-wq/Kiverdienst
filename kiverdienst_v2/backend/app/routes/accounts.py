# -*- coding: utf-8 -*-
"""Social Media Accounts API Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_pool

router = APIRouter()

class AccountCreate(BaseModel):
    platform: str
    brand_id: int
    username: str
    session_data: Optional[str] = None

@router.get("/")
async def list_accounts():
    """List all accounts"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT a.*, b.name as brand_name
            FROM accounts a
            LEFT JOIN brands b ON b.id = a.brand_id
            ORDER BY a.created_at DESC
        """)
        return [dict(row) for row in rows]

@router.post("/")
async def create_account(account: AccountCreate):
    """Create new account"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO accounts (platform, brand_id, username, session_data)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """, account.platform, account.brand_id, account.username, account.session_data)
        return dict(row)

@router.delete("/{account_id}/")
async def delete_account(account_id: int):
    """Delete account"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM accounts WHERE id = $1", account_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Account not found")
        return {"success": True, "message": "Account deleted"}
