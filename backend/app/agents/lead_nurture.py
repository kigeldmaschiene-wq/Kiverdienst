from .base_agent import BaseAgent
from typing import Dict, Any

class LeadNurtureAgent(BaseAgent):
    """Nurture leads through personalized engagement"""
    
    def __init__(self):
        super().__init__("LeadNurture")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        lead_id = task_data.get("lead_id")
        lead_data = task_data.get("lead_data", {})
        
        self.logger.info(f"Nurturing lead {lead_id}")
        
        # Analyze lead behavior
        behavior_analysis = self._analyze_behavior(lead_data)
        
        # Determine nurture strategy
        strategy = self._determine_strategy(behavior_analysis)
        
        # Generate personalized content
        content = self._generate_personalized_content(lead_data, strategy)
        
        # Calculate lead score
        lead_score = self._calculate_lead_score(lead_data, behavior_analysis)
        
        return {
            "lead_id": lead_id,
            "lead_score": lead_score,
            "strategy": strategy,
            "next_action": content,
            "ready_for_conversion": lead_score >= 75
        }
    
    def _analyze_behavior(self, lead_data: Dict) -> Dict:
        """Analyze lead behavior patterns"""
        email_opens = lead_data.get("email_opens", 0)
        email_clicks = lead_data.get("email_clicks", 0)
        website_visits = lead_data.get("website_visits", 0)
        engagement_level = lead_data.get("engagement_level", "low")
        
        return {
            "engagement_level": engagement_level,
            "email_engagement": email_opens / max(email_clicks, 1) if email_clicks else 0,
            "website_interest": website_visits,
            "days_subscribed": lead_data.get("days_subscribed", 0),
            "last_interaction": lead_data.get("last_interaction", "never")
        }
    
    def _determine_strategy(self, behavior: Dict) -> str:
        """Determine best nurture strategy"""
        engagement = behavior.get("engagement_level", "low")
        
        if engagement == "high":
            return "conversion_focused"
        elif engagement == "medium":
            return "value_building"
        else:
            return "re_engagement"
    
    def _generate_personalized_content(self, lead_data: Dict, strategy: str) -> Dict:
        """Generate personalized nurture content"""
        strategies = {
            "conversion_focused": {
                "type": "offer",
                "message": "Du bist bereit! Hier ist unser bestes Angebot.",
                "cta": "Jetzt starten"
            },
            "value_building": {
                "type": "educational",
                "message": "Hier sind 5 Tipps die dir sofort helfen",
                "cta": "Mehr erfahren"
            },
            "re_engagement": {
                "type": "attention",
                "message": "Wir vermissen dich! Schau was du verpasst hast",
                "cta": "Zur?ckkommen"
            }
        }
        
        return strategies.get(strategy, strategies["value_building"])
    
    def _calculate_lead_score(self, lead_data: Dict, behavior: Dict) -> int:
        """Calculate lead score (0-100)"""
        score = 0
        
        # Email engagement
        score += min(lead_data.get("email_opens", 0) * 5, 30)
        score += min(lead_data.get("email_clicks", 0) * 10, 30)
        
        # Website visits
        score += min(lead_data.get("website_visits", 0) * 8, 20)
        
        # Time as lead
        days = lead_data.get("days_subscribed", 0)
        if days > 7:
            score += 10
        if days > 30:
            score += 10
        
        return min(score, 100)
