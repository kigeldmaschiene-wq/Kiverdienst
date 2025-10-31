from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    platform: Optional[str] = None
    product_url: Optional[str] = None
    commission_rate: Optional[float] = None

@router.get("")
async def get_products():
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM products WHERE active = true ORDER BY name")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_product(product: ProductCreate):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            product_id = await conn.fetchval(
                """INSERT INTO products (name, description, price, category, platform, product_url, commission_rate) 
                   VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id""",
                product.name, product.description, product.price,
                product.category, product.platform, product.product_url, product.commission_rate
            )
        logger.info(f"Product created: {product_id}")
        return {"id": product_id, "success": True}
    except Exception as e:
        logger.error(f"Failed to create product: {e}")
        raise HTTPException(status_code=500, detail=str(e))
