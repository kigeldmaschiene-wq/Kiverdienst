from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Video(BaseModel):
    id: int
    brand_id: int
    character_id: Optional[int]
    platform: Optional[str]
    title: str
    script: Optional[str]
    status: str = 'draft'
    file_path: Optional[str]
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    engagement_rate: Optional[float]
    is_viral: bool = False
    posted_at: Optional[datetime]
    created_at: datetime
