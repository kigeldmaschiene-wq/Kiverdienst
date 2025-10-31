from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Product(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Optional[float]
    category: Optional[str]
    platform: Optional[str]
    product_url: Optional[str]
    commission_rate: Optional[float]
    active: bool = True
    created_at: datetime
