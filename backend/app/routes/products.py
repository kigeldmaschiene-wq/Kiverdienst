from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)
router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    commission_rate: float
    product_url: Optional[str] = None
    active: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    commission_rate: Optional[float] = None
    product_url: Optional[str] = None
    active: Optional[bool] = None

@router.get("/")
async def list_products():
    """Get all products"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            products = await conn.fetch("""
                SELECT p.*,
                       COUNT(DISTINCT ps.id) as sales_count,
                       COALESCE(SUM(ps.commission_earned), 0) as total_commission
                FROM products p
                LEFT JOIN product_sales ps ON ps.product_id = p.id
                GROUP BY p.id
                ORDER BY p.created_at DESC
            """)
            
            return [dict(p) for p in products]
    
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_product(product: ProductCreate):
    """Create new product"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO products (
                    name, description, price, commission_rate, product_url, active
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """, product.name, product.description, product.price,
                product.commission_rate, product.product_url, product.active
            )
            
            logger.info(f"Created product: {product.name}")
            return dict(result)
    
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    """Update product"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            updates = []
            values = []
            idx = 1
            
            for field, value in product.dict(exclude_unset=True).items():
                updates.append(f"{field} = ${idx}")
                values.append(value)
                idx += 1
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(product_id)
            query = f"UPDATE products SET {', '.join(updates)} WHERE id = ${idx} RETURNING *"
            
            result = await conn.fetchrow(query, *values)
            
            if not result:
                raise HTTPException(status_code=404, detail="Product not found")
            
            logger.info(f"Updated product: {product_id}")
            return dict(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """Delete product"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM products WHERE id = $1",
                product_id
            )
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Product not found")
            
            logger.info(f"Deleted product: {product_id}")
            return {"success": True, "message": "Product deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales")
async def get_sales_report():
    """Get sales report"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Total sales
            total_sales = await conn.fetchval("""
                SELECT COALESCE(SUM(sale_amount), 0) FROM product_sales
            """)
            
            # Total commission
            total_commission = await conn.fetchval("""
                SELECT COALESCE(SUM(commission_earned), 0) FROM product_sales
            """)
            
            # Sales by product
            by_product = await conn.fetch("""
                SELECT p.name, p.id,
                       COUNT(ps.id) as sales_count,
                       COALESCE(SUM(ps.sale_amount), 0) as total_amount,
                       COALESCE(SUM(ps.commission_earned), 0) as total_commission
                FROM products p
                LEFT JOIN product_sales ps ON ps.product_id = p.id
                GROUP BY p.id, p.name
                ORDER BY total_amount DESC
            """)
            
            # Recent sales
            recent_sales = await conn.fetch("""
                SELECT ps.*, p.name as product_name, b.name as brand_name
                FROM product_sales ps
                LEFT JOIN products p ON p.id = ps.product_id
                LEFT JOIN brands b ON b.id = ps.brand_id
                ORDER BY ps.sale_date DESC
                LIMIT 20
            """)
            
            return {
                "total_sales": float(total_sales) if total_sales else 0.0,
                "total_commission": float(total_commission) if total_commission else 0.0,
                "by_product": [dict(p) for p in by_product],
                "recent_sales": [dict(s) for s in recent_sales]
            }
    
    except Exception as e:
        logger.error(f"Error fetching sales report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
