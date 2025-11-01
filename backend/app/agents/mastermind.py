from .base_agent import BaseAgent
from ..utils.ollama_client import OllamaClient
from typing import Dict, Any
import json

class MastermindAgent(BaseAgent):
    """Strategic orchestrator using Ollama 70B model"""
    
    def __init__(self):
        super().__init__("Mastermind")
        self.ollama = OllamaClient()
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        brand_id = task_data.get("brand_id")
        action = task_data.get("action", "strategy")
        
        if action == "strategy":
            return await self._create_strategy(brand_id, task_data)
        elif action == "analyze":
            return await self._analyze_performance(brand_id, task_data)
        elif action == "optimize":
            return await self._optimize_campaigns(brand_id, task_data)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _create_strategy(self, brand_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create daily content strategy"""
        prompt = f"""Create a daily content strategy for a social media brand.
        
        Brand: {data.get('brand_name', 'Unknown')}
        Niche: {data.get('niche', 'General')}
        Target Platform: TikTok, Instagram, YouTube Shorts
        Videos Per Day: 7
        
        Generate 7 video ideas with:
        - Viral hook (3 seconds)
        - Compelling topic
        - Target keywords
        - Clear CTA
        
        Format as JSON array with: {{"hook": "...", "topic": "...", "keywords": ["..."], "cta": "..."}}
        """
        
        try:
            strategy = await self.ollama.generate(prompt, use_large=True, temperature=0.8)
            return {
                "strategy": strategy,
                "action": "strategy",
                "brand_id": brand_id
            }
        except Exception as e:
            self.logger.error(f"Strategy creation failed: {e}")
            # Return fallback strategy
            return {
                "strategy": self._get_fallback_strategy(),
                "action": "strategy",
                "brand_id": brand_id,
                "fallback": True
            }
    
    async def _analyze_performance(self, brand_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance and provide recommendations"""
        prompt = f"""Analyze social media performance data and provide optimization recommendations.
        
        Brand: {data.get('brand_name', 'Unknown')}
        Total Views: {data.get('total_views', 0)}
        Engagement Rate: {data.get('engagement_rate', 0)}%
        Video Count: {data.get('video_count', 0)}
        
        Analyze:
        1. What's working well?
        2. What needs improvement?
        3. Actionable recommendations for growth
        4. Content topics to focus on
        5. Posting time optimization
        
        Provide specific, actionable insights.
        """
        
        analysis = await self.ollama.generate(prompt, use_large=True)
        return {
            "analysis": analysis,
            "action": "analyze",
            "brand_id": brand_id
        }
    
    async def _optimize_campaigns(self, brand_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content campaigns"""
        prompt = f"""Optimize content campaign for maximum engagement and revenue.
        
        Current Performance:
        - Avg Views: {data.get('avg_views', 0)}
        - Avg Engagement: {data.get('avg_engagement', 0)}%
        - Revenue: ?{data.get('revenue', 0)}
        
        Provide optimization strategy for:
        1. Content themes
        2. Posting schedule
        3. Monetization tactics
        4. Audience targeting
        """
        
        optimization = await self.ollama.generate(prompt, use_large=True)
        return {
            "optimization": optimization,
            "action": "optimize",
            "brand_id": brand_id
        }
    
    def _get_fallback_strategy(self) -> str:
        """Fallback strategy when AI is unavailable"""
        return json.dumps([
            {
                "hook": "?? Diese KI spart dir 10 Stunden pro Woche!",
                "topic": "Produktivit?ts-KI-Tools",
                "keywords": ["KI", "Produktivit?t", "TimeManagement"],
                "cta": "Link in Bio f?r mehr Tools!"
            },
            {
                "hook": "?? So verdienst du online Geld - einfach erkl?rt!",
                "topic": "Online Geld verdienen f?r Anf?nger",
                "keywords": ["OnlineGeld", "PassivesEinkommen", "Affiliate"],
                "cta": "Folge f?r mehr Tipps!"
            }
        ])
