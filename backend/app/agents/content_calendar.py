from .base_agent import BaseAgent
from typing import Dict, Any, List
from datetime import datetime, timedelta

class ContentCalendarAgent(BaseAgent):
    """Manage content calendar and planning"""
    
    def __init__(self):
        super().__init__("ContentCalendar")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        brand_id = task_data.get("brand_id")
        weeks = task_data.get("weeks", 4)
        
        self.logger.info(f"Creating content calendar for {weeks} weeks")
        
        # Generate calendar
        calendar = self._generate_calendar(brand_id, weeks)
        
        # Add themes
        calendar = self._add_weekly_themes(calendar)
        
        return {
            "brand_id": brand_id,
            "weeks": weeks,
            "calendar": calendar
        }
    
    def _generate_calendar(self, brand_id: int, weeks: int) -> List[Dict]:
        """Generate content calendar"""
        calendar = []
        start_date = datetime.now()
        
        for week in range(weeks):
            week_start = start_date + timedelta(weeks=week)
            calendar.append({
                "week": week + 1,
                "start_date": week_start.strftime("%Y-%m-%d"),
                "videos_planned": 7,
                "status": "planned"
            })
        
        return calendar
    
    def _add_weekly_themes(self, calendar: List[Dict]) -> List[Dict]:
        """Add themes to calendar"""
        themes = [
            "Beginner Tips Week",
            "Expert Insights Week",
            "Product Review Week",
            "Behind The Scenes Week"
        ]
        
        for i, week in enumerate(calendar):
            week["theme"] = themes[i % len(themes)]
        
        return calendar
