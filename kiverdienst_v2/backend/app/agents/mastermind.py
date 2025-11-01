import json
import psycopg2.extras
from typing import Dict
from app.agents.base_agent import BaseAgent
from app.agents.utils.ollama_client import OllamaClient
from app.database import get_db

class MastermindAgent(BaseAgent):
    def __init__(self):
        super().__init__("Mastermind", "Strategic orchestrator")
        self.ollama = OllamaClient(model="llama3.1:70b")
    
    async def execute(self, task: str, context: Dict = None) -> Dict:
        context = context or {}
        
        if task == "select_topics":
            return await self.select_topics(context)
        else:
            raise ValueError(f"Unknown task: {task}")
    
    async def select_topics(self, context: Dict) -> Dict:
        with self.measure_time() as timer:
            try:
                brand_id = context['brand_id']
                count = context.get('count', 10)
                
                brand = self._get_brand(brand_id)
                if not brand:
                    raise ValueError(f"Brand {brand_id} not found")
                
                prompt = f"""
Select {count} viral topics for a {brand.get('niche', '')} content account.

Brand: {brand.get('name', '')}
Niche: {brand.get('niche', '')}

Output JSON:
{{
    "topics": [
        {{"topic": "...", "hook": "...", "reason": "..."}},
        ...
    ]
}}
"""
                
                response = self.ollama.generate(prompt, temperature=0.8)
                result = json.loads(response)
                topics = [t['topic'] for t in result.get('topics', [])]
                
                await self.log_action(
                    action="select_topics",
                    status="success",
                    message=f"Selected {len(topics)} topics",
                    details=result,
                    brand_id=brand_id,
                    duration_ms=timer.duration_ms
                )
                
                return {'success': True, 'data': {'topics': topics}}
                
            except Exception as e:
                await self.log_action(
                    action="select_topics",
                    status="failed",
                    message=str(e),
                    brand_id=context.get('brand_id'),
                    duration_ms=timer.duration_ms
                )
                return {'success': False, 'error': str(e)}
    
    def _get_brand(self, brand_id: int) -> Dict:
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM brands WHERE id = %s", (brand_id,))
        brand = cursor.fetchone()
        cursor.close()
        return dict(brand) if brand else {}
