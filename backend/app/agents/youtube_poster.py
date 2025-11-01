from .base_agent import BaseAgent
from typing import Dict, Any
import asyncio

class YouTubePosterAgent(BaseAgent):
    """Upload Shorts to YouTube"""
    
    def __init__(self):
        super().__init__("YouTubePoster")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        video_path = task_data.get("video_path")
        account_id = task_data.get("account_id")
        title = task_data.get("title", "")
        description = task_data.get("description", "")
        hashtags = task_data.get("hashtags", [])
        category = task_data.get("category", "22")  # 22 = People & Blogs
        
        if not video_path or not account_id:
            raise ValueError("video_path and account_id required")
        
        self.logger.info(f"Uploading Short to YouTube account {account_id}")
        
        # Build description with hashtags
        full_description = self._build_youtube_description(description, hashtags)
        
        try:
            post_url = await self._upload_to_youtube(
                video_path,
                account_id,
                title,
                full_description,
                category
            )
            
            return {
                "success": True,
                "platform": "youtube",
                "post_url": post_url,
                "account_id": account_id
            }
        
        except Exception as e:
            self.logger.error(f"YouTube upload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "youtube"
            }
    
    async def _upload_to_youtube(
        self, 
        video_path: str, 
        account_id: int, 
        title: str,
        description: str,
        category: str
    ) -> str:
        """Upload Short to YouTube (simulated)"""
        # In production: Use YouTube Data API v3
        # 1. Authenticate with OAuth2
        # 2. Upload video using videos.insert
        # 3. Set as Short (#Shorts in title/description)
        # 4. Set visibility (public/unlisted/scheduled)
        # 5. Add to playlist
        
        await asyncio.sleep(2)
        
        return f"https://youtube.com/shorts/ABC123xyz"
    
    def _build_youtube_description(self, description: str, hashtags: list) -> str:
        """Build YouTube description with hashtags"""
        # YouTube Shorts best practices:
        # - Include #Shorts
        # - Use up to 15 hashtags (first 3 show above title)
        # - Add timestamps
        # - Include links
        
        hashtags_str = " ".join([f"#{tag}" for tag in hashtags[:15]])
        
        full_description = f"""{description}

#Shorts {hashtags_str}

---
?? Folge uns f?r mehr Content!
?? Aktiviere die Glocke f?r Updates
?? Kommentiere deine Meinung

? {self._get_year()} - Alle Rechte vorbehalten
"""
        
        return full_description
    
    def _optimize_title(self, title: str) -> str:
        """Optimize title for YouTube algorithm"""
        # YouTube best practices:
        # - 60-70 characters ideal
        # - Include #Shorts
        # - Use emojis sparingly
        # - Front-load keywords
        
        if "#Shorts" not in title and "#shorts" not in title:
            title = f"{title} #Shorts"
        
        if len(title) > 100:
            title = title[:97] + "..."
        
        return title
    
    def _get_year(self) -> int:
        """Get current year"""
        from datetime import datetime
        return datetime.now().year
