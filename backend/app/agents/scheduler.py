from .base_agent import BaseAgent
from typing import Dict, Any, List
from datetime import datetime, timedelta

class SchedulerAgent(BaseAgent):
    """Schedule and manage content posting times"""
    
    def __init__(self):
        super().__init__("Scheduler")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        brand_id = task_data.get("brand_id")
        videos_per_day = task_data.get("videos_per_day", 7)
        platforms = task_data.get("platforms", ["tiktok", "instagram", "youtube"])
        
        self.logger.info(f"Creating posting schedule for brand {brand_id}")
        
        # Generate optimal posting times
        schedule = self._generate_schedule(videos_per_day, platforms)
        
        # Optimize for each platform
        optimized_schedule = self._optimize_by_platform(schedule, platforms)
        
        return {
            "brand_id": brand_id,
            "schedule": optimized_schedule,
            "videos_per_day": videos_per_day,
            "platforms": platforms
        }
    
    def _generate_schedule(self, videos_per_day: int, platforms: List[str]) -> List[Dict]:
        """Generate posting schedule"""
        # Best posting times (German timezone)
        best_times = ["08:00", "12:00", "15:00", "18:00", "20:00", "21:00", "22:00"]
        
        schedule = []
        for i in range(videos_per_day):
            time = best_times[i % len(best_times)]
            schedule.append({
                "slot": i + 1,
                "time": time,
                "platform": platforms[i % len(platforms)]
            })
        
        return schedule
    
    def _optimize_by_platform(self, schedule: List[Dict], platforms: List[str]) -> Dict:
        """Optimize schedule by platform"""
        platform_schedules = {}
        
        for platform in platforms:
            platform_posts = [s for s in schedule if s["platform"] == platform]
            platform_schedules[platform] = {
                "posts_per_day": len(platform_posts),
                "posting_times": [p["time"] for p in platform_posts],
                "best_days": ["Monday", "Wednesday", "Friday", "Sunday"]
            }
        
        return platform_schedules
