from .base_agent import BaseAgent
from typing import Dict, Any

class ContentGeneratorAgent(BaseAgent):
    """Generates video scripts and content ideas"""
    
    def __init__(self):
        super().__init__("ContentGenerator")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        """Generate content based on brand and topic"""
        # Future: Call Ollama for script generation
        return {"script": "Generated script placeholder"}
