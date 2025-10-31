from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Character(BaseModel):
    id: int
    name: str
    brand_id: int
    gender: Optional[str]
    character_type: Optional[str]
    description: Optional[str]
    personality: Optional[str]
    voice_id: Optional[str]
    voice_provider: str = 'azure'
    clips_count: int = 0
    created_at: datetime
