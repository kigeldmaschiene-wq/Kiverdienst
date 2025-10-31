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
    voice_id: Optional[str] = None
    library_path: Optional[str] = None
    base_prompt: Optional[str] = None
    personality: Optional[str] = None

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    character_type: Optional[str] = None
    voice_id: Optional[str] = None
    library_path: Optional[str] = None
    base_prompt: Optional[str] = None
    personality: Optional[str] = None

@router.get("/")
async def list_characters():
    """Get all characters"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            characters = await conn.fetch("""
                SELECT c.*, b.name as brand_name,
                       COUNT(cc.id) as clips_count
                FROM characters c
                LEFT JOIN brands b ON b.id = c.brand_id
                LEFT JOIN character_clips cc ON cc.character_id = c.id
                GROUP BY c.id, b.name
                ORDER BY c.created_at DESC
            """)
            
            return [dict(char) for char in characters]
    
    except Exception as e:
        logger.error(f"Error fetching characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}")
async def get_brand_characters(brand_id: int):
    """Get characters for specific brand"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            characters = await conn.fetch("""
                SELECT c.*,
                       COUNT(cc.id) as clips_count
                FROM characters c
                LEFT JOIN character_clips cc ON cc.character_id = c.id
                WHERE c.brand_id = $1
                GROUP BY c.id
                ORDER BY c.created_at DESC
            """, brand_id)
            
            return [dict(char) for char in characters]
    
    except Exception as e:
        logger.error(f"Error fetching brand characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{character_id}")
async def get_character(character_id: int):
    """Get character by ID"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            character = await conn.fetchrow("""
                SELECT c.*, b.name as brand_name
                FROM characters c
                LEFT JOIN brands b ON b.id = c.brand_id
                WHERE c.id = $1
            """, character_id)
            
            if not character:
                raise HTTPException(status_code=404, detail="Character not found")
            
            return dict(character)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching character: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_character(character: CharacterCreate):
    """Create new character"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO characters (
                    name, brand_id, gender, character_type, voice_id,
                    library_path, base_prompt, personality
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
            """, character.name, character.brand_id, character.gender,
                character.character_type, character.voice_id, character.library_path,
                character.base_prompt, character.personality
            )
            
            logger.info(f"Created character: {character.name}")
            return dict(result)
    
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{character_id}")
async def update_character(character_id: int, character: CharacterUpdate):
    """Update character"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            updates = []
            values = []
            idx = 1
            
            for field, value in character.dict(exclude_unset=True).items():
                updates.append(f"{field} = ${idx}")
                values.append(value)
                idx += 1
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(character_id)
            query = f"UPDATE characters SET {', '.join(updates)} WHERE id = ${idx} RETURNING *"
            
            result = await conn.fetchrow(query, *values)
            
            if not result:
                raise HTTPException(status_code=404, detail="Character not found")
            
            logger.info(f"Updated character: {character_id}")
            return dict(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating character: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{character_id}")
async def delete_character(character_id: int):
    """Delete character"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM characters WHERE id = $1",
                character_id
            )
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Character not found")
            
            logger.info(f"Deleted character: {character_id}")
            return {"success": True, "message": "Character deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting character: {e}")
        raise HTTPException(status_code=500, detail=str(e))
