from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ContentPlanCreate(BaseModel):
    brand_id: int
    theme: str
    keywords: Optional[str] = None
    target_topics: Optional[str] = None

@router.get("/plans")
async def get_content_plans(brand_id: Optional[int] = None):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            if brand_id:
                rows = await conn.fetch(
                    "SELECT * FROM content_plans WHERE brand_id = $1 ORDER BY week_start_date DESC",
                    brand_id
                )
            else:
                rows = await conn.fetch("SELECT * FROM content_plans ORDER BY week_start_date DESC")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get content plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plans")
async def create_content_plan(plan: ContentPlanCreate):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            plan_id = await conn.fetchval(
                """INSERT INTO content_plans (brand_id, theme, keywords, target_topics, week_start_date) 
                   VALUES ($1, $2, $3, $4, CURRENT_DATE) RETURNING id""",
                plan.brand_id, plan.theme, plan.keywords, plan.target_topics
            )
        logger.info(f"Content plan created: {plan_id}")
        return {"id": plan_id, "success": True}
    except Exception as e:
        logger.error(f"Failed to create content plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
