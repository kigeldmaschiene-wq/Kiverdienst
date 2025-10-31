from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Brand(BaseModel):
    id: int
    name: str
    niche: Optional[str]
    tagline: Optional[str]
    description: Optional[str]
    content_mode: str = 'character'
    active: bool = False
    tiktok_enabled: bool = False
    tiktok_username: Optional[str]
    instagram_enabled: bool = False
    instagram_username: Optional[str]
    youtube_enabled: bool = False
    youtube_username: Optional[str]
    videos_per_day: int = 7
    created_at: datetime
