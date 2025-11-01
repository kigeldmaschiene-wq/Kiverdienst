# -*- coding: utf-8 -*-
"""Characters API Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_pool

router = APIRouter()

class CharacterCreate(BaseModel):
    brand_id: int
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    character_type: Optional[str] = None
    voice_id: Optional[str] = None

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    character_type: Optional[str] = None
    voice_id: Optional[str] = None

@router.get("/")
async def list_characters():
    """List all characters"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT c.*, b.name as brand_name,
                   COUNT(v.id) as clips_count
            FROM characters c
            LEFT JOIN brands b ON b.id = c.brand_id
            LEFT JOIN videos v ON v.character_id = c.id
            GROUP BY c.id, b.name
            ORDER BY c.created_at DESC
        """)
        return [dict(row) for row in rows]

@router.post("/")
async def create_character(character: CharacterCreate):
    """Create new character"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO characters (brand_id, name, age, gender, character_type, voice_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """, character.brand_id, character.name, character.age, character.gender,
            character.character_type, character.voice_id)
        return dict(row)

@router.put("/{character_id}/")
async def update_character(character_id: int, character: CharacterUpdate):
    """Update character"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        updates = []
        values = []
        idx = 1
        for key, value in character.dict(exclude_unset=True).items():
            updates.append(f"{key} = ${idx}")
            values.append(value)
            idx += 1
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(character_id)
        query = f"UPDATE characters SET {', '.join(updates)} WHERE id = ${idx} RETURNING *"
        row = await conn.fetchrow(query, *values)
        
        if not row:
            raise HTTPException(status_code=404, detail="Character not found")
        return dict(row)

@router.delete("/{character_id}/")
async def delete_character(character_id: int):
    """Delete character"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM characters WHERE id = $1", character_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Character not found")
        return {"success": True, "message": "Character deleted"}
