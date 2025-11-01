from .base_agent import BaseAgent
from ..utils.ollama_client import OllamaClient
from typing import Dict, Any, List
import random

class TrendAnalyzerAgent(BaseAgent):
    """Identify and analyze trending topics"""
    
    def __init__(self):
        super().__init__("TrendAnalyzer")
        self.ollama = OllamaClient()
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        niche = task_data.get("niche", "general")
        platform = task_data.get("platform", "tiktok")
        region = task_data.get("region", "de")
        
        self.logger.info(f"Analyzing trends for {niche} on {platform}")
        
        # Collect trending topics
        trends = await self._collect_trends(niche, platform, region)
        
        # Analyze each trend
        analyzed_trends = []
        for trend in trends:
            analysis = await self._analyze_trend(trend, niche)
            analyzed_trends.append(analysis)
        
        # Rank by potential
        analyzed_trends.sort(key=lambda x: x["potential_score"], reverse=True)
        
        return {
            "niche": niche,
            "platform": platform,
            "trends": analyzed_trends[:20],
            "total_found": len(analyzed_trends)
        }
    
    async def _collect_trends(self, niche: str, platform: str, region: str) -> List[Dict]:
        """Collect trending topics (simulated)"""
        # In production: Scrape trending page, use APIs
        
        # Simulated trending topics by niche
        niche_trends = {
            "KI & Online Business": [
                "ChatGPT Prompts die dein Leben ver?ndern",
                "Mit KI in 2025 Geld verdienen",
                "Passive Einkommensstr?me durch Automation",
                "Beste KI Tools f?r Content Creator",
                "Online Business starten ohne Startkapital",
                "KI ersetzt diese Jobs 2025",
                "Midjourney vs DALL-E 3",
                "Wie ich mit KI 10k/Monat verdiene",
                "No-Code Tools f?r Anf?nger",
                "KI Marketing Strategien"
            ],
            "Finanzen & Sparen": [
                "Spartipps die wirklich funktionieren",
                "Mit 100? reich werden",
                "Diese Ausgaben sind sinnlos",
                "ETF Portfolio f?r Anf?nger",
                "Steuer Tricks die keiner kennt",
                "So sparst du 1000? pro Monat",
                "Finanzielle Freiheit mit 30",
                "Beste Sparapps 2025",
                "Inflation besiegen Strategie",
                "Von 0 auf 10k sparen"
            ],
            "Haustiere & Katzen": [
                "S??este Katzen Momente",
                "Katze tut lustige Dinge",
                "Katzen vs Gurken Reaktion",
                "Maine Coon K?tzchen",
                "Katze lernt Tricks",
                "Unerwartete Katzen Fails",
                "Warum Katzen das tun",
                "Katze trifft Baby",
                "Rasse Katzen Vergleich",
                "Katzen Pflege Tipps"
            ],
            "ASMR & Entspannung": [
                "Rain sounds for sleeping",
                "Tapping ASMR Compilation",
                "No talking ASMR",
                "Slime ASMR satisfying",
                "Whisper ASMR deutsch",
                "Nature sounds 10 hours",
                "Meditation f?r Anf?nger",
                "Deep sleep frequency",
                "Stress abbauen schnell",
                "Achtsamkeit ?bungen"
            ]
        }
        
        topics = niche_trends.get(niche, niche_trends["KI & Online Business"])
        
        return [
            {
                "topic": topic,
                "platform": platform,
                "mentions": random.randint(1000, 100000),
                "growth_rate": random.uniform(1.2, 5.0)
            }
            for topic in topics
        ]
    
    async def _analyze_trend(self, trend: Dict, niche: str) -> Dict:
        """Analyze trend potential"""
        topic = trend["topic"]
        
        # Calculate potential score
        mentions = trend.get("mentions", 0)
        growth_rate = trend.get("growth_rate", 1.0)
        
        # Score based on mentions and growth
        mention_score = min(mentions / 1000, 100)
        growth_score = growth_rate * 20
        potential_score = (mention_score + growth_score) / 2
        
        # Analyze competition
        competition = self._assess_competition(mentions)
        
        # Generate content angles
        angles = await self._generate_content_angles(topic, niche)
        
        return {
            "topic": topic,
            "potential_score": min(potential_score, 100),
            "mentions": mentions,
            "growth_rate": growth_rate,
            "competition": competition,
            "content_angles": angles,
            "recommended_hashtags": self._generate_hashtags(topic)
        }
    
    def _assess_competition(self, mentions: int) -> str:
        """Assess competition level"""
        if mentions < 5000:
            return "low"
        elif mentions < 50000:
            return "medium"
        else:
            return "high"
    
    async def _generate_content_angles(self, topic: str, niche: str) -> List[str]:
        """Generate content angle ideas"""
        # Use AI to generate angles (fallback to templates)
        try:
            prompt = f"Generate 3 unique content angles for topic '{topic}' in niche '{niche}'. Short bullets only."
            response = await self.ollama.generate(prompt, use_large=False, temperature=0.8)
            
            # Parse response
            angles = [line.strip("- ") for line in response.split("\n") if line.strip()]
            return angles[:3]
        except:
            # Fallback angles
            return [
                f"Pers?nliche Erfahrung mit {topic}",
                f"Top 5 Tipps zu {topic}",
                f"H?ufige Fehler bei {topic}"
            ]
    
    def _generate_hashtags(self, topic: str) -> List[str]:
        """Generate relevant hashtags"""
        words = topic.lower().split()
        hashtags = [word for word in words if len(word) > 3]
        
        # Add generic high-performing hashtags
        hashtags.extend(["viral", "foryou", "trending", "fyp"])
        
        return hashtags[:10]
