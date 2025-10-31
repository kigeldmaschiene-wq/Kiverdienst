import httpx
import os
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for Ollama AI API"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://135.181.129.240:11434")
        self.model_large = os.getenv("OLLAMA_MODEL_LARGE", "llama3.1:70b")
        self.model_fast = os.getenv("OLLAMA_MODEL_FAST", "llama3.1:8b-instruct-q8_0")
        self.timeout = httpx.Timeout(120.0, connect=10.0)
    
    async def generate(self, prompt: str, use_large: bool = False, temperature: float = 0.7):
        """Generate text using Ollama"""
        model = self.model_large if use_large else self.model_fast
        logger.info(f"Generating with {model}...")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "top_p": 0.9
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["response"]
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise Exception("AI generation timed out. Please try again.")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise Exception(f"AI generation failed: {str(e)}")
    
    async def chat(self, messages: list, use_large: bool = False):
        """Chat with Ollama using message history"""
        model = self.model_large if use_large else self.model_fast
        logger.info(f"Chat with {model}...")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise Exception(f"AI chat failed: {str(e)}")
