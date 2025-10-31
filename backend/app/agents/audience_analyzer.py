from .base_agent import BaseAgent
from typing import Dict, Any
import random

class AudienceAnalyzerAgent(BaseAgent):
    """Analyze audience demographics and behavior"""
    
    def __init__(self):
        super().__init__("AudienceAnalyzer")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        brand_id = task_data.get("brand_id")
        platform = task_data.get("platform", "tiktok")
        
        self.logger.info(f"Analyzing audience for brand {brand_id}")
        
        # Collect audience data
        demographics = self._analyze_demographics()
        behavior = self._analyze_behavior()
        interests = self._analyze_interests()
        
        # Generate persona
        persona = self._generate_persona(demographics, behavior, interests)
        
        return {
            "brand_id": brand_id,
            "demographics": demographics,
            "behavior": behavior,
            "interests": interests,
            "persona": persona
        }
    
    def _analyze_demographics(self) -> Dict:
        """Analyze audience demographics"""
        return {
            "age_range": "18-34",
            "gender_split": {"male": 45, "female": 53, "other": 2},
            "top_locations": ["Germany", "Austria", "Switzerland"],
            "language": "German"
        }
    
    def _analyze_behavior(self) -> Dict:
        """Analyze audience behavior"""
        return {
            "peak_active_hours": ["20:00-22:00", "12:00-14:00"],
            "avg_watch_time": random.uniform(15, 35),
            "engagement_rate": random.uniform(0.05, 0.15),
            "sharing_behavior": "high"
        }
    
    def _analyze_interests(self) -> list:
        """Analyze audience interests"""
        return ["technology", "business", "finance", "self-improvement"]
    
    def _generate_persona(self, demographics, behavior, interests) -> Dict:
        """Generate audience persona"""
        return {
            "name": "Tech-Savvy Millennial",
            "age": "25-32",
            "goals": ["Learn new skills", "Earn more money", "Stay updated"],
            "pain_points": ["Limited time", "Information overload", "Need practical tips"]
        }
