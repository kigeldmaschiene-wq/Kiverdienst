"""
Mastermind Agent - Main Orchestrator
Uses Llama 3.1 70B for strategic decisions

This is the CEO of the system that:
- Analyzes brand performance
- Decides video allocation per brand
- Selects viral topics based on trends
- Makes budget decisions
- Provides AI approval recommendations
"""
import json
from typing import Dict, List, Optional
from app.agents.base_agent import BaseAgent
from app.agents.utils.ollama_client import OllamaClient
from app.database import get_pool

class MastermindAgent(BaseAgent):
    """
    Mastermind Agent - Strategic Orchestrator
    
    Tasks:
    - select_topics: Choose viral topics for brand
    - allocate_videos: Decide videos per brand per day
    - daily_briefing: Morning strategic decisions (future)
    - approve_recommendation: AI approval logic (future)
    """
    
    def __init__(self):
        super().__init__(
            name="Mastermind",
            description="Strategic orchestrator using Llama 70B"
        )
        self.ollama = OllamaClient(model="llama3.1:70b")
        
        # Check if Ollama is available
        if not self.ollama.check_health():
            self.logger.warning("Ollama 70B not available - Mastermind will fail!")
    
    async def execute(self, task: str, context: Dict = None) -> Dict:
        """
        Execute mastermind task
        
        Args:
            task: Task name
                - 'select_topics': Choose topics for brand
                - 'allocate_videos': Decide videos per brand
            context: Task-specific context
        
        Returns:
            Dict with success status and data
        """
        context = context or {}
        
        try:
            if task == "select_topics":
                return await self.select_topics(context)
            elif task == "allocate_videos":
                return await self.allocate_videos_per_brand()
            else:
                raise ValueError(f"Unknown task: {task}")
        except Exception as e:
            self.logger.error(f"Mastermind task '{task}' failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def select_topics(self, context: Dict) -> Dict:
        """
        Select viral topics for video generation
        
        Args:
            context: {
                'brand_id': int,
                'count': int (default: 10)
            }
        
        Returns:
            Dict with:
            {
                'success': True/False,
                'data': {
                    'topics': List[str],
                    'details': List[Dict] (with hooks and reasons)
                }
            }
        """
        with self.measure_time() as timer:
            try:
                brand_id = context['brand_id']
                count = context.get('count', 10)
                
                # Get brand info
                brand = await self._get_brand(brand_id)
                
                if not brand:
                    raise ValueError(f"Brand {brand_id} not found")
                
                # Get trending topics (TODO: TikTok Creative Center API)
                trending = self._get_trending_topics(brand.get('niche', ''))
                
                # Build prompt for Llama 70B
                prompt = f"""
You are selecting viral topics for a {brand.get('niche', '')} content account.

Brand: {brand.get('name', '')}
Niche: {brand.get('niche', '')}
Target Audience: General audience 18-35
Tone: Engaging and authentic

Trending Topics in Niche:
{json.dumps(trending, indent=2)}

Task: Select {count} best topics for today's videos.

Consider:
- Viral potential (trending + proven hooks)
- Brand fit (matches niche and tone)
- Audience interest (what they want to see)
- Monetization potential (can we sell something related?)

Output JSON format:
{{
    "topics": [
        {{
            "topic": "3 AI tools that save 5 hours per day",
            "hook": "Stop wasting time on...",
            "reason": "High search volume + clear value proposition"
        }},
        {{
            "topic": "Make $500/month with ChatGPT",
            "hook": "This makes $500/month",
            "reason": "Money angle + specific number = viral"
        }}
    ]
}}
"""
                
                # Generate with Ollama
                response = self.ollama.generate(prompt, temperature=0.8)
                
                # Extract JSON
                try:
                    result = json.loads(response)
                except:
                    # Try to extract JSON from markdown
                    if "```json" in response:
                        start = response.index("```json") + 7
                        end = response.index("```", start)
                        result = json.loads(response[start:end].strip())
                    else:
                        raise ValueError("Could not extract JSON from response")
                
                topics = [t['topic'] for t in result.get('topics', [])]
                
                # Log success
                await self.log_action(
                    action="select_topics",
                    status="success",
                    message=f"Selected {len(topics)} topics",
                    details=result,
                    brand_id=brand_id,
                    duration_ms=timer.duration_ms
                )
                
                return {
                    'success': True,
                    'data': {
                        'topics': topics,
                        'details': result.get('topics', [])
                    }
                }
                
            except Exception as e:
                self.logger.error(f"Topic selection failed: {e}")
                
                await self.log_action(
                    action="select_topics",
                    status="failed",
                    message=str(e),
                    brand_id=context.get('brand_id'),
                    duration_ms=timer.duration_ms
                )
                
                return {
                    'success': False,
                    'error': str(e)
                }
    
    async def allocate_videos_per_brand(self) -> Dict:
        """
        Decide how many videos each brand gets today
        
        Based on:
        - Recent performance (avg views last 7 days)
        - Brand status (active)
        - Budget constraints (future)
        
        Returns:
            Dict with:
            {
                'success': True/False,
                'data': {
                    brand_id: videos_count,
                    ...
                }
            }
        """
        with self.measure_time() as timer:
            try:
                pool = await get_pool()
                
                async with pool.acquire() as conn:
                    # Get all active brands
                    brands = await conn.fetch("SELECT * FROM brands WHERE active = TRUE")
                    
                    allocation = {}
                    
                    for brand in brands:
                        # Get recent performance
                        perf = await conn.fetchrow("""
                            SELECT 
                                AVG(views) as avg_views, 
                                AVG(likes) as avg_likes,
                                COUNT(*) as video_count
                            FROM videos
                            WHERE brand_id = $1 
                            AND created_at > NOW() - INTERVAL '7 days'
                        """, brand['id'])
                        
                        # Default allocation
                        videos_today = 7
                        
                        # Adjust based on performance
                        if perf and perf['video_count'] > 0:
                            avg_views = perf['avg_views'] or 0
                            
                            if avg_views > 10000:
                                videos_today = 10  # Viral brand!
                            elif avg_views > 5000:
                                videos_today = 8
                            elif avg_views > 1000:
                                videos_today = 7
                            elif avg_views > 500:
                                videos_today = 6
                            else:
                                videos_today = 5  # Low performer
                        
                        allocation[brand['id']] = videos_today
                
                # Log success
                await self.log_action(
                    action="allocate_videos",
                    status="success",
                    message=f"Allocated videos for {len(allocation)} brands",
                    details=allocation,
                    duration_ms=timer.duration_ms
                )
                
                return {
                    'success': True,
                    'data': allocation
                }
                
            except Exception as e:
                self.logger.error(f"Video allocation failed: {e}")
                
                await self.log_action(
                    action="allocate_videos",
                    status="failed",
                    message=str(e),
                    duration_ms=timer.duration_ms
                )
                
                return {
                    'success': False,
                    'error': str(e)
                }
    
    # Helper methods
    
    async def _get_brand(self, brand_id: int) -> Dict:
        """Get brand details from database"""
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", brand_id)
            return dict(brand) if brand else {}
    
    def _get_trending_topics(self, niche: str) -> List[Dict]:
        """
        Get trending topics for niche
        
        TODO: Implement TikTok Creative Center API integration
        For now returns mock data based on niche
        """
        # Mock data - replace with actual TikTok API call
        mock_topics = {
            'Technology': [
                {"topic": "ChatGPT productivity hacks", "volume": 1500000, "growth": "+45%"},
                {"topic": "AI tools for video editing", "volume": 890000, "growth": "+32%"},
                {"topic": "Make money with AI in 2025", "volume": 750000, "growth": "+28%"},
            ],
            'Finance': [
                {"topic": "Budget apps that actually work", "volume": 950000, "growth": "+38%"},
                {"topic": "Side hustles that pay instantly", "volume": 820000, "growth": "+25%"},
                {"topic": "Passive income ideas 2025", "volume": 700000, "growth": "+22%"},
            ],
            'Health & Fitness': [
                {"topic": "30 day fitness challenge results", "volume": 850000, "growth": "+40%"},
                {"topic": "Meal prep for weight loss", "volume": 680000, "growth": "+28%"},
                {"topic": "Best supplements for energy", "volume": 550000, "growth": "+20%"},
            ],
            'default': [
                {"topic": "Trending topic 1", "volume": 500000, "growth": "+20%"},
                {"topic": "Trending topic 2", "volume": 400000, "growth": "+15%"},
                {"topic": "Trending topic 3", "volume": 300000, "growth": "+10%"},
            ]
        }
        
        return mock_topics.get(niche, mock_topics['default'])
