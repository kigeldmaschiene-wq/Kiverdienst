from .base_agent import BaseAgent
from typing import Dict, Any, List
import random

class CompetitorMonitorAgent(BaseAgent):
    """Monitor competitor accounts and strategies"""
    
    def __init__(self):
        super().__init__("CompetitorMonitor")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        niche = task_data.get("niche")
        platform = task_data.get("platform", "tiktok")
        competitor_usernames = task_data.get("competitors", [])
        
        self.logger.info(f"Monitoring {len(competitor_usernames)} competitors in {niche}")
        
        # If no competitors provided, discover them
        if not competitor_usernames:
            competitor_usernames = await self._discover_competitors(niche, platform)
        
        # Analyze each competitor
        competitor_data = []
        for username in competitor_usernames[:10]:
            data = await self._analyze_competitor(username, platform, niche)
            competitor_data.append(data)
        
        # Extract insights
        insights = self._extract_insights(competitor_data)
        
        return {
            "niche": niche,
            "platform": platform,
            "competitors_analyzed": len(competitor_data),
            "competitors": competitor_data,
            "insights": insights
        }
    
    async def _discover_competitors(self, niche: str, platform: str) -> List[str]:
        """Discover top competitors in niche"""
        # In production: Search by hashtags, scrape top accounts
        
        # Simulated competitor accounts
        niche_competitors = {
            "KI & Online Business": [
                "ki_hustle_master", "ai_money_maker", "tech_entrepreneur",
                "online_business_pro", "passive_income_ai", "automation_expert"
            ],
            "Finanzen & Sparen": [
                "finanz_guru", "spar_tipps_daily", "money_saver_de",
                "invest_smart", "budget_queen", "reich_werden_einfach"
            ],
            "Haustiere & Katzen": [
                "cat_lover_daily", "cute_kittens_world", "cat_behavior_pro",
                "feline_friends", "meow_moments", "kitty_paradise"
            ]
        }
        
        return niche_competitors.get(niche, niche_competitors["KI & Online Business"])
    
    async def _analyze_competitor(self, username: str, platform: str, niche: str) -> Dict:
        """Analyze single competitor account"""
        # In production: Scrape profile, analyze posts
        
        return {
            "username": username,
            "platform": platform,
            "followers": random.randint(10000, 1000000),
            "avg_views": random.randint(5000, 500000),
            "avg_engagement_rate": random.uniform(0.05, 0.20),
            "posting_frequency": random.randint(3, 14),  # per week
            "content_types": self._identify_content_types(),
            "top_hashtags": self._extract_top_hashtags(niche),
            "best_posting_times": ["08:00", "12:00", "18:00", "21:00"],
            "avg_video_length": random.randint(15, 45),
            "growth_rate": random.uniform(1.1, 3.5)
        }
    
    def _identify_content_types(self) -> List[str]:
        """Identify content types used"""
        types = ["educational", "entertainment", "product_review", "tutorial", 
                 "behind_the_scenes", "trending", "Q&A", "story_time"]
        return random.sample(types, k=random.randint(3, 5))
    
    def _extract_top_hashtags(self, niche: str) -> List[str]:
        """Extract commonly used hashtags"""
        base_hashtags = ["fyp", "viral", "trending", "foryou"]
        
        niche_hashtags = {
            "KI & Online Business": ["ai", "tech", "business", "entrepreneur", "automation"],
            "Finanzen & Sparen": ["money", "finance", "saving", "investing", "wealth"],
            "Haustiere & Katzen": ["cats", "cute", "pets", "kitten", "catlover"]
        }
        
        return base_hashtags + niche_hashtags.get(niche, [])
    
    def _extract_insights(self, competitor_data: List[Dict]) -> Dict:
        """Extract actionable insights from competitor analysis"""
        if not competitor_data:
            return {}
        
        # Calculate averages
        avg_followers = sum(c["followers"] for c in competitor_data) / len(competitor_data)
        avg_engagement = sum(c["avg_engagement_rate"] for c in competitor_data) / len(competitor_data)
        avg_frequency = sum(c["posting_frequency"] for c in competitor_data) / len(competitor_data)
        
        # Extract common patterns
        all_hashtags = []
        all_content_types = []
        for comp in competitor_data:
            all_hashtags.extend(comp.get("top_hashtags", []))
            all_content_types.extend(comp.get("content_types", []))
        
        # Count frequency
        from collections import Counter
        hashtag_counts = Counter(all_hashtags)
        content_counts = Counter(all_content_types)
        
        return {
            "avg_follower_count": int(avg_followers),
            "avg_engagement_rate": round(avg_engagement, 3),
            "recommended_posting_frequency": int(avg_frequency),
            "most_effective_hashtags": [tag for tag, _ in hashtag_counts.most_common(10)],
            "best_content_types": [ct for ct, _ in content_counts.most_common(5)],
            "opportunity_score": self._calculate_opportunity(competitor_data)
        }
    
    def _calculate_opportunity(self, competitor_data: List[Dict]) -> float:
        """Calculate market opportunity score"""
        # Lower competition + higher engagement = higher opportunity
        avg_followers = sum(c["followers"] for c in competitor_data) / len(competitor_data)
        avg_engagement = sum(c["avg_engagement_rate"] for c in competitor_data) / len(competitor_data)
        
        # Inverse follower count (less followers = more opportunity)
        follower_score = max(0, 100 - (avg_followers / 10000))
        
        # High engagement is good
        engagement_score = avg_engagement * 500
        
        opportunity = (follower_score + engagement_score) / 2
        return min(opportunity, 100)
