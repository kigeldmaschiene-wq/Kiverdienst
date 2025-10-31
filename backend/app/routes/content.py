from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_pool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ScriptGenerateRequest(BaseModel):
    topic: str
    brand_id: int
    niche: Optional[str] = None
    style: Optional[str] = "engaging"

class TopicAnalyzeRequest(BaseModel):
    topic: str
    niche: Optional[str] = None

@router.post("/generate-script")
async def generate_script(request: ScriptGenerateRequest):
    """Generate TikTok script using AI"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Get brand info
            brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", request.brand_id)
            
            if not brand:
                raise HTTPException(status_code=404, detail="Brand not found")
            
            # Create agent task for script generation
            task = await conn.fetchrow("""
                INSERT INTO agent_tasks (
                    agent_name, task_type, task_data, status
                ) VALUES ('ContentGenerator', 'generate_script', $1, 'pending')
                RETURNING *
            """, {
                "topic": request.topic,
                "brand_id": request.brand_id,
                "brand_name": brand['name'],
                "niche": request.niche or brand['niche'],
                "style": request.style
            })
            
            # For demo purposes, return a sample script
            # In production, this would wait for the agent to complete
            sample_script = {
                "hook": f"?? {request.topic} - Du wirst nicht glauben was passiert!",
                "body": f"Hier erf?hrst du alles ?ber {request.topic}. Diese 3 Tipps werden dein Leben ver?ndern...",
                "cta": "Folge f?r mehr! Link in Bio ??",
                "hashtags": ["#viral", "#trending", f"#{request.niche or 'lifestyle'}"]
            }
            
            logger.info(f"Generated script for topic: {request.topic}")
            return {
                "success": True,
                "task_id": task['id'],
                "script": sample_script,
                "status": "generated"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating script: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-topic")
async def analyze_topic(request: TopicAnalyzeRequest):
    """Analyze topic potential"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Create analysis task
            task = await conn.fetchrow("""
                INSERT INTO agent_tasks (
                    agent_name, task_type, task_data, status
                ) VALUES ('TrendAnalyzer', 'analyze_topic', $1, 'pending')
                RETURNING *
            """, {
                "topic": request.topic,
                "niche": request.niche
            })
            
            # Sample analysis result
            analysis = {
                "topic": request.topic,
                "potential_score": 8.5,
                "trend_status": "rising",
                "competition": "medium",
                "recommended_hashtags": ["#trending", "#viral", f"#{request.topic.lower()}"],
                "best_posting_times": ["08:00", "12:00", "18:00", "21:00"],
                "estimated_reach": "10k-50k",
                "engagement_prediction": "high"
            }
            
            logger.info(f"Analyzed topic: {request.topic}")
            return {
                "success": True,
                "task_id": task['id'],
                "analysis": analysis
            }
    
    except Exception as e:
        logger.error(f"Error analyzing topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending")
async def get_trending_content():
    """Get trending content ideas"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Get recent trending topics
            trends = await conn.fetch("""
                SELECT t.*, n.niche_name
                FROM trending_topics t
                LEFT JOIN niches n ON n.id = t.niche_id
                WHERE t.detected_at >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY t.trend_score DESC
                LIMIT 20
            """)
            
            # If no trends in database, return sample trends
            if not trends:
                sample_trends = [
                    {"topic": "KI Tools f?r Content Creation", "trend_score": 9.2, "hashtags": "#KI #ContentCreation"},
                    {"topic": "Passive Einkommensstr?me 2025", "trend_score": 8.8, "hashtags": "#PassivEinkommen #OnlineBusiness"},
                    {"topic": "Spartipps f?r den Alltag", "trend_score": 8.5, "hashtags": "#Sparen #Finanzen"},
                    {"topic": "S??e Katzen Momente", "trend_score": 9.0, "hashtags": "#Katzen #Cute"},
                    {"topic": "ASMR Entspannung", "trend_score": 8.3, "hashtags": "#ASMR #Relaxation"}
                ]
                return {"trends": sample_trends, "source": "sample"}
            
            return {"trends": [dict(t) for t in trends], "source": "database"}
    
    except Exception as e:
        logger.error(f"Error fetching trending content: {e}")
        raise HTTPException(status_code=500, detail=str(e))
