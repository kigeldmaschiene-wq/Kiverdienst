from .base_agent import BaseAgent
from typing import Dict, Any
import asyncio

class InstagramPosterAgent(BaseAgent):
    """Upload Reels to Instagram"""
    
    def __init__(self):
        super().__init__("InstagramPoster")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        video_path = task_data.get("video_path")
        account_id = task_data.get("account_id")
        caption = task_data.get("caption", "")
        hashtags = task_data.get("hashtags", [])
        cover_frame = task_data.get("cover_frame", 0)
        
        if not video_path or not account_id:
            raise ValueError("video_path and account_id required")
        
        self.logger.info(f"Uploading Reel to Instagram account {account_id}")
        
        # Build caption with hashtags (max 30 hashtags)
        full_caption = self._build_instagram_caption(caption, hashtags[:30])
        
        try:
            post_url = await self._upload_to_instagram(
                video_path,
                account_id,
                full_caption,
                cover_frame
            )
            
            return {
                "success": True,
                "platform": "instagram",
                "post_url": post_url,
                "account_id": account_id
            }
        
        except Exception as e:
            self.logger.error(f"Instagram upload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram"
            }
    
    async def _upload_to_instagram(
        self, 
        video_path: str, 
        account_id: int, 
        caption: str,
        cover_frame: int
    ) -> str:
        """Upload Reel to Instagram (simulated)"""
        # In production: Use Instagram Graph API or Playwright
        # 1. Authenticate with account
        # 2. Upload video as Reel
        # 3. Set cover frame
        # 4. Add caption with hashtags
        # 5. Publish
        
        await asyncio.sleep(2)
        
        return f"https://www.instagram.com/reel/ABC123XYZ/"
    
    def _build_instagram_caption(self, caption: str, hashtags: list) -> str:
        """Build Instagram caption with hashtags"""
        # Instagram best practices:
        # - Caption first, hashtags at the end
        # - Line break between caption and hashtags
        # - Max 2200 characters total
        
        hashtags_str = " ".join([f"#{tag}" for tag in hashtags])
        full_caption = f"{caption}\n.\n.\n.\n{hashtags_str}"
        
        # Trim if too long
        if len(full_caption) > 2200:
            full_caption = full_caption[:2197] + "..."
        
        return full_caption
    
    def _select_cover_frame(self, video_path: str) -> int:
        """Select best frame for Reel cover"""
        # In production: Use CV to find most engaging frame
        # - Face detection
        # - Visual appeal
        # - Text readability
        
        # For now, use frame at 2 seconds
        return 60  # Frame 60 at 30fps = 2 seconds
