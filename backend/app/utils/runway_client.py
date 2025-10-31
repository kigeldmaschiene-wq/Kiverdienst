import httpx
import logging
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)

class RunwayClient:
    """Client for Runway Gen-3 API"""
    
    def __init__(self):
        self.api_key = settings.runway_api_key
        self.base_url = "https://api.runwayml.com/v1"
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        image_path: Optional[str] = None
    ) -> Dict:
        """Generate video using Runway Gen-3"""
        if not self.api_key:
            logger.warning("Runway API key not configured")
            return {"error": "API key missing"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "duration": duration
            }
            
            if image_path:
                payload["image"] = image_path
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Runway generation failed: {e}")
            return {"error": str(e)}
