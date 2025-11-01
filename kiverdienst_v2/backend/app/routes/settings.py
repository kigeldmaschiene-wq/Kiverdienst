# -*- coding: utf-8 -*-
"""Settings API Routes - MISSING ROUTE #2"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.database import get_pool
import json

router = APIRouter()

class SettingsUpdate(BaseModel):
    settings: Dict[str, Any]

@router.get("/")
async def get_settings():
    """Get all settings"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT key, value FROM settings")
        settings = {}
        for row in rows:
            try:
                # Try to parse JSON values
                settings[row['key']] = json.loads(row['value'])
            except:
                # Fallback to string value
                settings[row['key']] = row['value']
        
        # Return with defaults if empty
        if not settings:
            settings = {
                "ollama_url": "http://host.docker.internal:11434",
                "runway_api_key": "",
                "azure_tts_key": "",
                "azure_tts_region": "westeurope",
                "database_url": "postgresql://postgres:***@postgres:5432/kiverdienst_v2",
                "auto_posting": True,
                "auto_script_generation": True,
                "analytics_tracking": True,
                "posting_interval": 4,
                "budget_limit": 1000,
                "notify_80": True,
                "notify_90": True,
                "pause_at_100": True,
                "impressum": "",
                "privacy_template": "standard",
                "cookie_consent": True,
                "ollama_main_model": "llama3.1:70b",
                "ollama_temperature": 0.7
            }
        
        return settings

@router.post("/")
async def update_settings(update: SettingsUpdate):
    """Update settings"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        for key, value in update.settings.items():
            # Convert value to JSON string for storage
            value_str = json.dumps(value) if not isinstance(value, str) else value
            
            await conn.execute("""
                INSERT INTO settings (key, value, updated_at)
                VALUES ($1, $2, CURRENT_TIMESTAMP)
                ON CONFLICT (key) 
                DO UPDATE SET value = $2, updated_at = CURRENT_TIMESTAMP
            """, key, value_str)
        
        return {"success": True, "message": "Settings updated"}
