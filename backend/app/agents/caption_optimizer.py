from .base_agent import BaseAgent
from ..utils.ollama_client import OllamaClient
from typing import Dict, Any

class CaptionOptimizerAgent(BaseAgent):
    """Optimize captions for maximum engagement"""
    
    def __init__(self):
        super().__init__("CaptionOptimizer")
        self.ollama = OllamaClient()
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        original_caption = task_data.get("caption", "")
        platform = task_data.get("platform", "tiktok")
        
        # Optimize caption
        optimized = await self._optimize_caption(original_caption, platform)
        
        # A/B test variants
        variants = await self._generate_variants(optimized)
        
        return {
            "original": original_caption,
            "optimized": optimized,
            "variants": variants,
            "platform": platform
        }
    
    async def _optimize_caption(self, caption: str, platform: str) -> str:
        """Optimize caption for platform"""
        prompt = f"""Optimize this {platform} caption for maximum engagement:
        "{caption}"
        
        Rules: Short, punchy, with emoji, under 150 chars"""
        
        try:
            optimized = await self.ollama.generate(prompt, use_large=False)
            return optimized.strip()[:150]
        except:
            return caption
    
    async def _generate_variants(self, caption: str) -> list:
        """Generate A/B test variants"""
        return [caption, f"?? {caption}", f"{caption} ??"]
