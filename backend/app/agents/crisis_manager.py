from .base_agent import BaseAgent
from typing import Dict, Any

class CrisisManagerAgent(BaseAgent):
    """Manage brand crises and negative situations"""
    
    def __init__(self):
        super().__init__("CrisisManager")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        brand_id = task_data.get("brand_id")
        crisis_type = task_data.get("crisis_type", "negative_comments")
        
        self.logger.warning(f"Crisis detected for brand {brand_id}: {crisis_type}")
        
        # Assess severity
        severity = self._assess_severity(crisis_type)
        
        # Generate response plan
        response_plan = self._create_response_plan(crisis_type, severity)
        
        # Create damage control measures
        damage_control = self._create_damage_control()
        
        return {
            "brand_id": brand_id,
            "crisis_type": crisis_type,
            "severity": severity,
            "response_plan": response_plan,
            "damage_control": damage_control
        }
    
    def _assess_severity(self, crisis_type: str) -> str:
        """Assess crisis severity"""
        high_severity = ["legal_issue", "major_scandal", "data_breach"]
        if crisis_type in high_severity:
            return "high"
        elif crisis_type == "viral_negative":
            return "medium"
        else:
            return "low"
    
    def _create_response_plan(self, crisis_type: str, severity: str) -> Dict:
        """Create crisis response plan"""
        return {
            "immediate_actions": [
                "Pause all scheduled content",
                "Monitor situation closely",
                "Prepare official statement"
            ],
            "communication_strategy": "transparent and honest",
            "timeline": "24-48 hours"
        }
    
    def _create_damage_control(self) -> list:
        """Create damage control measures"""
        return [
            "Issue public apology if needed",
            "Engage positively with community",
            "Share corrective actions taken",
            "Increase positive content frequency"
        ]
