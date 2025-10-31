from .base_agent import BaseAgent
from ..utils.ollama_client import OllamaClient
from typing import Dict, Any
import json

class ContentGeneratorAgent(BaseAgent):
    """Generate TikTok scripts using Ollama 8B model"""
    
    def __init__(self):
        super().__init__("ContentGenerator")
        self.ollama = OllamaClient()
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        topic = task_data.get("topic")
        brand = task_data.get("brand_name", "")
        niche = task_data.get("niche", "")
        style = task_data.get("style", "engaging")
        
        prompt = f"""Write a TikTok video script for:
        
        Topic: {topic}
        Brand: {brand}
        Niche: {niche}
        Style: {style}
        
        Structure (30-40 seconds total):
        1. HOOK (3 seconds): Attention-grabbing opening that stops scrolling
        2. BODY (30-35 seconds): Value-packed content with clear points
        3. CTA (5 seconds): Clear call-to-action
        
        Requirements:
        - Use simple, conversational German
        - Include pattern interrupts
        - Create curiosity
        - Provide value
        - End with strong CTA
        
        Format as JSON:
        {{
            "hook": "...",
            "body": "...",
            "cta": "...",
            "hashtags": ["tag1", "tag2", "tag3"],
            "estimated_duration": 35
        }}
        """
        
        try:
            script_json = await self.ollama.generate(prompt, use_large=False, temperature=0.8)
            
            # Try to parse JSON, fallback to structured text
            try:
                script = json.loads(script_json)
            except:
                # Create structured response from text
                script = self._parse_text_to_script(script_json, topic)
            
            return {
                "script": script,
                "topic": topic,
                "brand": brand
            }
        
        except Exception as e:
            self.logger.error(f"Script generation failed: {e}")
            # Return fallback script
            return {
                "script": self._get_fallback_script(topic, brand),
                "topic": topic,
                "brand": brand,
                "fallback": True
            }
    
    def _parse_text_to_script(self, text: str, topic: str) -> Dict[str, Any]:
        """Parse text response into structured script"""
        lines = text.split('\n')
        
        return {
            "hook": f"?? {topic} - Du musst das sehen!",
            "body": text[:200] if len(text) > 200 else text,
            "cta": "Folge f?r mehr! Link in Bio ??",
            "hashtags": ["#viral", "#trending", "#foryou"],
            "estimated_duration": 35
        }
    
    def _get_fallback_script(self, topic: str, brand: str) -> Dict[str, Any]:
        """Fallback script when generation fails"""
        return {
            "hook": f"?? {topic} - Das wird dein Leben ver?ndern!",
            "body": f"Heute zeige ich dir alles ?ber {topic}. Diese 3 Dinge musst du wissen: 1. Es ist einfacher als du denkst. 2. Du kannst sofort starten. 3. Die Ergebnisse sind erstaunlich.",
            "cta": "Folge mir f?r mehr Tipps! Link in Bio ??",
            "hashtags": ["#viral", "#trending", "#foryou", f"#{brand.lower().replace(' ', '')}"],
            "estimated_duration": 35
        }
