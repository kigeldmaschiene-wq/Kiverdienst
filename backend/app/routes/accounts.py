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

@router.get("")
async def get_accounts(brand_id: Optional[int] = None):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            if brand_id:
                rows = await conn.fetch(
                    "SELECT * FROM accounts WHERE brand_id = $1 ORDER BY platform",
                    brand_id
                )
            else:
                rows = await conn.fetch("SELECT * FROM accounts ORDER BY platform")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_account(account: AccountCreate):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            account_id = await conn.fetchval(
                """INSERT INTO accounts (brand_id, platform, username) 
                   VALUES ($1, $2, $3) RETURNING id""",
                account.brand_id, account.platform, account.username
            )
        logger.info(f"Account created: {account_id}")
        return {"id": account_id, "success": True}
    except Exception as e:
        logger.error(f"Failed to create account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{account_id}")
async def delete_account(account_id: int):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM accounts WHERE id = $1", account_id)
        logger.info(f"Account deleted: {account_id}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to delete account {account_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
