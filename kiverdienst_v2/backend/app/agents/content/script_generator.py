import json
import psycopg2.extras
from typing import Dict
from app.agents.base_agent import BaseAgent
from app.agents.utils.ollama_client import OllamaClient
from app.database import get_db

class ScriptGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("ScriptGenerator", "Video script generation")
        self.ollama = OllamaClient(model="llama3.1:8b")
    
    async def execute(self, topic: str, brand_id: int, context: Dict = None) -> Dict:
        context = context or {}
        
        with self.measure_time() as timer:
            try:
                brand = self._get_brand(brand_id)
                if not brand:
                    raise ValueError(f"Brand {brand_id} not found")
                
                prompt = f"""
Write viral TikTok script for: {topic}

Brand: {brand.get('name', '')}
Niche: {brand.get('niche', '')}

Output JSON:
{{
    "hook": "...",
    "problem": "...",
    "story": "...",
    "cta": "...",
    "full_script": "..."
}}
"""
                
                response = self.ollama.generate(prompt, temperature=0.8)
                script_data = json.loads(response)
                
                script_id = self._save_script(script_data, brand_id)
                script_data['id'] = script_id
                
                await self.log_action(
                    action="generate_script",
                    status="success",
                    message=f"Script generated: {topic}",
                    brand_id=brand_id,
                    duration_ms=timer.duration_ms
                )
                
                return {'success': True, 'data': script_data}
                
            except Exception as e:
                await self.log_action(
                    action="generate_script",
                    status="failed",
                    message=str(e),
                    brand_id=brand_id,
                    duration_ms=timer.duration_ms
                )
                return {'success': False, 'error': str(e)}
    
    def _save_script(self, script: Dict, brand_id: int) -> int:
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            INSERT INTO video_scripts 
            (brand_id, hook, problem, story, cta, full_script, word_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (brand_id, script['hook'], script.get('problem', ''),
              script['story'], script['cta'], script['full_script'],
              len(script['full_script'].split())))
        
        script_id = cursor.fetchone()['id']
        db.commit()
        cursor.close()
        return script_id
    
    def _get_brand(self, brand_id: int) -> Dict:
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM brands WHERE id = %s", (brand_id,))
        brand = cursor.fetchone()
        cursor.close()
        return dict(brand) if brand else {}
