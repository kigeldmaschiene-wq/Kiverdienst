from .base_agent import BaseAgent
from typing import Dict, Any, List

class ContentRecyclerAgent(BaseAgent):
    """Repurpose and recycle top-performing content"""
    
    def __init__(self):
        super().__init__("ContentRecycler")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        brand_id = task_data.get("brand_id")
        min_views = task_data.get("min_views", 10000)
        
        self.logger.info(f"Finding content to recycle for brand {brand_id}")
        
        # Find top performers
        top_content = self._find_top_performers(brand_id, min_views)
        
        # Generate recycling ideas
        recycling_ideas = self._generate_recycling_ideas(top_content)
        
        return {
            "brand_id": brand_id,
            "top_content_count": len(top_content),
            "recycling_ideas": recycling_ideas
        }
    
    def _find_top_performers(self, brand_id: int, min_views: int) -> List[Dict]:
        """Find top performing content"""
        import random
        return [
            {
                "video_id": i,
                "title": f"Top Video {i}",
                "views": random.randint(min_views, min_views * 10),
                "engagement_rate": random.uniform(0.10, 0.20)
            }
            for i in range(1, 6)
        ]
    
    def _generate_recycling_ideas(self, content: List[Dict]) -> List[Dict]:
        """Generate ideas for recycling content"""
        ideas = []
        for video in content:
            ideas.append({
                "original_video": video["video_id"],
                "recycling_methods": [
                    "Create carousel post for Instagram",
                    "Turn into blog post",
                    "Create email newsletter",
                    "Update with new information"
                ]
            })
        return ideas
