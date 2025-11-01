"""
Ollama Client - Interface to local Llama models
Supports both Llama 70B (strategic) and 8B (production)
"""
import requests
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Client for interacting with Ollama API
    
    Usage:
        # For strategic decisions (Mastermind)
        client = OllamaClient(model="llama3.1:70b")
        
        # For production (Script Generation)
        client = OllamaClient(model="llama3.1:8b")
        
        response = client.generate("Write a script about...")
    """
    
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.8,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text with Ollama
        
        Args:
            prompt: The prompt text
            temperature: Randomness 0.0-1.0 (0.0=deterministic, 1.0=creative)
            max_tokens: Max response length
            system: System prompt (optional)
            stream: Stream response (default: False)
        
        Returns:
            Generated text
        
        Raises:
            Exception: If Ollama request fails
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system:
                payload["system"] = system
            
            logger.info(f"Ollama request: model={self.model}, temp={temperature}, tokens={max_tokens}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=180  # 3 minutes max
            )
            
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if 'response' in data:
                            full_response += data['response']
                return full_response
            else:
                # Non-streaming
                result = response.json()
                generated_text = result['response']
                
                logger.info(f"Ollama response: {len(generated_text)} chars, model={self.model}")
                
                return generated_text
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out after 180 seconds")
            raise Exception("Ollama generation timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: int = 4096,
        system: Optional[str] = None
    ) -> Dict:
        """
        Generate JSON response
        Automatically extracts JSON from response
        
        Args:
            prompt: Prompt (should ask for JSON output)
            temperature: Randomness
            max_tokens: Max length
            system: System prompt
        
        Returns:
            Parsed JSON dict
        
        Raises:
            ValueError: If JSON cannot be extracted
        """
        response = self.generate(prompt, temperature, max_tokens, system)
        
        # Try to extract JSON
        try:
            # Method 1: Look for JSON between ```json and ```
            if "```json" in response:
                start = response.index("```json") + 7
                end = response.index("```", start)
                json_str = response[start:end].strip()
                return json.loads(json_str)
            
            # Method 2: Look for JSON between { and }
            if "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
                return json.loads(json_str)
            
            # Method 3: Try parsing entire response
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Failed to extract JSON from response: {e}")
            logger.debug(f"Response was: {response[:1000]}")
            raise ValueError(f"Could not parse JSON from Ollama response: {e}")
    
    def check_health(self) -> bool:
        """
        Check if Ollama is running and model is available
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if self.model in model_names:
                logger.info(f"Ollama health check OK - model {self.model} available")
                return True
            else:
                logger.warning(f"Model {self.model} not found. Available: {model_names}")
                return False
            
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
