from .base_agent import BaseAgent
from typing import Dict, Any
import asyncio

class TikTokPosterAgent(BaseAgent):
    """Upload videos to TikTok using automation"""
    
    def __init__(self):
        super().__init__("TikTokPoster")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        video_path = task_data.get("video_path")
        account_id = task_data.get("account_id")
        caption = task_data.get("caption", "")
        hashtags = task_data.get("hashtags", [])
        schedule_time = task_data.get("schedule_time")
        
        if not video_path or not account_id:
            raise ValueError("video_path and account_id required")
        
        self.logger.info(f"Uploading to TikTok account {account_id}")
        
        # Build full caption with hashtags
        full_caption = self._build_caption(caption, hashtags)
        
        # Simulate upload (in production, use Playwright/Selenium)
        try:
            post_url = await self._upload_to_tiktok(
                video_path,
                account_id,
                full_caption,
                schedule_time
            )
            
            return {
                "success": True,
                "platform": "tiktok",
                "post_url": post_url,
                "account_id": account_id,
                "scheduled": schedule_time is not None
            }
        
        except Exception as e:
            self.logger.error(f"TikTok upload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "tiktok"
            }
    
    async def _upload_to_tiktok(
        self, 
        video_path: str, 
        account_id: int, 
        caption: str,
        schedule_time: str = None
    ) -> str:
        """Upload video to TikTok (simulated)"""
        # In production: Use Playwright browser automation
        # 1. Login to TikTok
        # 2. Navigate to upload page
        # 3. Select video file
        # 4. Add caption and hashtags
        # 5. Schedule or post immediately
        # 6. Extract post URL
        
        # Simulate upload delay
        await asyncio.sleep(2)
        
        # Return simulated post URL
        return f"https://www.tiktok.com/@account{account_id}/video/1234567890"
    
    def _build_caption(self, caption: str, hashtags: list) -> str:
        """Build full caption with hashtags"""
        hashtags_str = " ".join([f"#{tag}" for tag in hashtags])
        return f"{caption}\n\n{hashtags_str}"
    
    def _optimize_caption(self, caption: str) -> str:
        """Optimize caption for TikTok algorithm"""
        # Keep under 150 characters for best engagement
        if len(caption) > 150:
            caption = caption[:147] + "..."
        
        # Add emoji if not present
        if not any(char in caption for char in "?????????"):
            caption = f"?? {caption}"
        
        return caption
