from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CharacterCreate(BaseModel):
    name: str
    brand_id: int
    gender: Optional[str] = None
    character_type: Optional[str] = None
    description: Optional[str] = None
    personality: Optional[str] = None

@router.get("")
async def get_characters(brand_id: Optional[int] = None):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            if brand_id:
                rows = await conn.fetch(
                    "SELECT * FROM characters WHERE brand_id = $1 ORDER BY name", 
                    brand_id
                )
            else:
                rows = await conn.fetch("SELECT * FROM characters ORDER BY name")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{character_id}")
async def get_character(character_id: int):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM characters WHERE id = $1", character_id
            )
            if not row:
                raise HTTPException(status_code=404, detail="Character not found")
            return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_character(character: CharacterCreate):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            char_id = await conn.fetchval(
                """INSERT INTO characters (name, brand_id, gender, character_type, description, personality) 
                   VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""",
                character.name, character.brand_id, 
                character.gender, character.character_type,
                character.description, character.personality
            )
        logger.info(f"Character created: {char_id}")
        return {"id": char_id, "success": True}
    except Exception as e:
        logger.error(f"Failed to create character: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{character_id}")
async def delete_character(character_id: int):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM characters WHERE id = $1", character_id)
        logger.info(f"Character deleted: {character_id}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to delete character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
