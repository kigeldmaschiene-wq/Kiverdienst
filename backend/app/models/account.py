from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Account(BaseModel):
    id: int
    brand_id: int
    platform: str
    username: str
    status: str = 'active'
    followers: int = 0
    posting_mode: str = 'auto'
    videos_per_day: int = 7
    last_post_at: Optional[datetime]
    created_at: datetime
