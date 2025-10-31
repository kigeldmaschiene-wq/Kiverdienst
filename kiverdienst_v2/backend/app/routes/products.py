# -*- coding: utf-8 -*-
"""Products API Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.database import get_pool

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    commission_percent: Decimal
    affiliate_link: str
    niche: str
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    commission_percent: Optional[Decimal] = None
    affiliate_link: Optional[str] = None
    niche: Optional[str] = None
    image_url: Optional[str] = None

@router.get("/")
async def list_products():
    """List all products"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM products ORDER BY created_at DESC")
        return [dict(row) for row in rows]

@router.post("/")
async def create_product(product: ProductCreate):
    """Create new product"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO products (name, description, price, commission_percent, affiliate_link, niche, image_url)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """, product.name, product.description, product.price, product.commission_percent,
            product.affiliate_link, product.niche, product.image_url)
        return dict(row)

@router.put("/{product_id}/")
async def update_product(product_id: int, product: ProductUpdate):
    """Update product"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        updates = []
        values = []
        idx = 1
        for key, value in product.dict(exclude_unset=True).items():
            updates.append(f"{key} = ${idx}")
            values.append(value)
            idx += 1
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(product_id)
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ${idx} RETURNING *"
        row = await conn.fetchrow(query, *values)
        
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")
        return dict(row)

@router.delete("/{product_id}/")
async def delete_product(product_id: int):
    """Delete product"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM products WHERE id = $1", product_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Product not found")
        return {"success": True, "message": "Product deleted"}
