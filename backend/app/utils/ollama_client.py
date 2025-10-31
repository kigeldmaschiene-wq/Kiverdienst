import httpx
import logging
from typing import Optional, Dict, Any
from ..config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama LLM"""
    
    def __init__(self):
        self.base_url = settings.ollama_url
        self.model_large = settings.ollama_model_large
        self.model_fast = settings.ollama_model_fast
    
    async def generate(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate text using Ollama"""
        try:
            model = model or self.model_fast
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""
    
    async def chat(
        self,
        messages: list,
        model: Optional[str] = None
    ) -> str:
        """Chat completion using Ollama"""
        try:
            model = model or self.model_fast
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            return ""
