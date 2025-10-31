from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class AccountCreate(BaseModel):
    brand_id: int
    platform: str
    username: str
    status: str = "active"
    proxy_config: Optional[str] = None
    session_data: Optional[str] = None

class AccountUpdate(BaseModel):
    username: Optional[str] = None
    status: Optional[str] = None
    followers: Optional[int] = None
    proxy_config: Optional[str] = None
    session_data: Optional[str] = None

@router.get("/")
async def list_accounts():
    """Get all social media accounts"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            accounts = await conn.fetch("""
                SELECT a.*, b.name as brand_name
                FROM accounts a
                LEFT JOIN brands b ON b.id = a.brand_id
                ORDER BY a.created_at DESC
            """)
            
            return [dict(acc) for acc in accounts]
    
    except Exception as e:
        logger.error(f"Error fetching accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}")
async def get_brand_accounts(brand_id: int):
    """Get accounts for specific brand"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            accounts = await conn.fetch("""
                SELECT * FROM accounts
                WHERE brand_id = $1
                ORDER BY platform
            """, brand_id)
            
            return [dict(acc) for acc in accounts]
    
    except Exception as e:
        logger.error(f"Error fetching brand accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_account(account: AccountCreate):
    """Add new social media account"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO accounts (
                    brand_id, platform, username, status, proxy_config, session_data
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """, account.brand_id, account.platform, account.username,
                account.status, account.proxy_config, account.session_data
            )
            
            logger.info(f"Created account: {account.username} on {account.platform}")
            return dict(result)
    
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{account_id}")
async def update_account(account_id: int, account: AccountUpdate):
    """Update account"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            updates = []
            values = []
            idx = 1
            
            for field, value in account.dict(exclude_unset=True).items():
                updates.append(f"{field} = ${idx}")
                values.append(value)
                idx += 1
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(account_id)
            query = f"UPDATE accounts SET {', '.join(updates)} WHERE id = ${idx} RETURNING *"
            
            result = await conn.fetchrow(query, *values)
            
            if not result:
                raise HTTPException(status_code=404, detail="Account not found")
            
            logger.info(f"Updated account: {account_id}")
            return dict(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{account_id}")
async def delete_account(account_id: int):
    """Remove account"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM accounts WHERE id = $1",
                account_id
            )
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Account not found")
            
            logger.info(f"Deleted account: {account_id}")
            return {"success": True, "message": "Account deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))
