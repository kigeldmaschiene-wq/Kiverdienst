import httpx
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RunwayClient:
    """Client for Runway Gen-3 API"""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY")
        self.base_url = "https://api.runwayml.com/v1"
        self.timeout = httpx.Timeout(300.0, connect=10.0)
        
        if not self.api_key:
            logger.warning("RUNWAY_API_KEY not set - video generation will fail")
    
    async def generate_video(
        self, 
        image_path: str, 
        prompt: str, 
        duration: int = 5,
        model: str = "gen3a_turbo"
    ) -> dict:
        """Generate video from image using Runway Gen-3"""
        if not self.api_key:
            raise ValueError("RUNWAY_API_KEY not configured")
        
        logger.info(f"Generating video with Runway Gen-3...")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Upload image
                with open(image_path, 'rb') as f:
                    files = {'image': f}
                    response = await client.post(
                        f"{self.base_url}/images",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        files=files
                    )
                    response.raise_for_status()
                    image_id = response.json()["id"]
                
                # Generate video
                response = await client.post(
                    f"{self.base_url}/generations",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": model,
                        "image_id": image_id,
                        "prompt": prompt,
                        "duration": duration
                    }
                )
                response.raise_for_status()
                
                logger.info("Video generation started successfully")
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Runway API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Video generation failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Runway generation failed: {e}")
            raise Exception(f"Video generation failed: {str(e)}")
    
    async def get_generation_status(self, generation_id: str) -> dict:
        """Check status of video generation"""
        if not self.api_key:
            raise ValueError("RUNWAY_API_KEY not configured")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/generations/{generation_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get generation status: {e}")
            raise
