import requests
import json
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def generate(self, prompt: str, temperature: float = 0.8, 
                 max_tokens: int = 4096, system: str = None) -> str:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system:
                payload["system"] = system
            
            logger.info(f"Ollama: model={self.model}, temp={temperature}")
            
            response = requests.post(self.api_url, json=payload, timeout=180)
            response.raise_for_status()
            
            return response.json()['response']
            
        except Exception as e:
            logger.error(f"Ollama failed: {e}")
            raise
    
    def check_health(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return True
        except:
            return False
