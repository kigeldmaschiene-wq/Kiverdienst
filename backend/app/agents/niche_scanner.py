from .base_agent import BaseAgent
from ..utils.ollama_client import OllamaClient
from typing import Dict, Any, List
import random

class NicheScannerAgent(BaseAgent):
    """Scan and evaluate new niche opportunities"""
    
    def __init__(self):
        super().__init__("NicheScanner")
        self.ollama = OllamaClient()
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        criteria = task_data.get("criteria", {})
        min_potential = criteria.get("min_potential", 60)
        max_competition = criteria.get("max_competition", 70)
        
        self.logger.info("Scanning for profitable niches")
        
        # Discover potential niches
        niches = await self._discover_niches()
        
        # Evaluate each niche
        evaluated_niches = []
        for niche in niches:
            evaluation = await self._evaluate_niche(niche)
            
            # Filter by criteria
            if (evaluation["potential_score"] >= min_potential and 
                evaluation["competition_score"] <= max_competition):
                evaluated_niches.append(evaluation)
        
        # Sort by profitability
        evaluated_niches.sort(key=lambda x: x["profitability_score"], reverse=True)
        
        return {
            "niches_found": len(evaluated_niches),
            "top_niches": evaluated_niches[:10],
            "criteria": criteria
        }
    
    async def _discover_niches(self) -> List[str]:
        """Discover potential niches using AI"""
        prompt = """Generate 20 profitable social media content niches for 2025.
        Focus on: high engagement, monetization potential, growing trends.
        One niche per line, German market friendly."""
        
        try:
            response = await self.ollama.generate(prompt, use_large=True, temperature=0.9)
            niches = [line.strip("- ").strip() for line in response.split("\n") if line.strip()]
            return niches[:20]
        except:
            # Fallback niches
            return [
                "KI & Automation f?r Alltag",
                "Passive Einkommensstr?me",
                "Minimalismus & Decluttering",
                "Haustier Training Tipps",
                "Schnelle Rezepte unter 10 Min",
                "Finanzen f?r Gen Z",
                "Home Workout ohne Ger?te",
                "Productivity Hacks",
                "Nachhaltiges Leben",
                "Mental Health & Achtsamkeit",
                "Side Hustle Ideen",
                "Crypto f?r Anf?nger",
                "Reisen mit Budget",
                "DIY & Upcycling",
                "Gaming News & Tips",
                "Fashion auf Budget",
                "Tech Reviews Deutsch",
                "Eltern Hacks",
                "Karriere Tipps",
                "Self-Improvement Daily"
            ]
    
    async def _evaluate_niche(self, niche: str) -> Dict:
        """Evaluate niche profitability"""
        # Simulate niche metrics
        search_volume = random.randint(1000, 100000)
        avg_cpm = random.uniform(2.0, 15.0)
        competition_level = random.choice(["low", "medium", "high"])
        
        # Calculate scores
        potential_score = self._calculate_potential(search_volume, avg_cpm)
        competition_score = self._calculate_competition_score(competition_level)
        monetization_score = self._calculate_monetization(niche, avg_cpm)
        profitability_score = (potential_score + monetization_score - competition_score) / 2
        
        # Generate content ideas
        content_ideas = await self._generate_content_ideas(niche)
        
        # Identify monetization methods
        monetization_methods = self._identify_monetization(niche)
        
        return {
            "niche": niche,
            "potential_score": round(potential_score, 1),
            "competition_score": round(competition_score, 1),
            "monetization_score": round(monetization_score, 1),
            "profitability_score": round(profitability_score, 1),
            "search_volume": search_volume,
            "avg_cpm": round(avg_cpm, 2),
            "competition_level": competition_level,
            "content_ideas": content_ideas,
            "monetization_methods": monetization_methods,
            "estimated_monthly_revenue": self._estimate_revenue(profitability_score)
        }
    
    def _calculate_potential(self, search_volume: int, avg_cpm: float) -> float:
        """Calculate potential score"""
        volume_score = min((search_volume / 1000), 100)
        cpm_score = min((avg_cpm * 5), 100)
        return (volume_score + cpm_score) / 2
    
    def _calculate_competition_score(self, level: str) -> float:
        """Calculate competition score (higher = more competition)"""
        scores = {"low": 30, "medium": 60, "high": 90}
        return scores.get(level, 60)
    
    def _calculate_monetization(self, niche: str, avg_cpm: float) -> float:
        """Calculate monetization potential"""
        # High CPM niches score higher
        cpm_score = min(avg_cpm * 6, 100)
        
        # Check if niche has products/services
        product_keywords = ["business", "money", "tech", "finance", "health", "fitness"]
        has_products = any(kw in niche.lower() for kw in product_keywords)
        
        product_score = 30 if has_products else 0
        
        return (cpm_score + product_score) / 1.3
    
    async def _generate_content_ideas(self, niche: str) -> List[str]:
        """Generate content ideas for niche"""
        try:
            prompt = f"Generate 5 viral content ideas for niche: {niche}. Short titles only."
            response = await self.ollama.generate(prompt, use_large=False)
            ideas = [line.strip("- ").strip() for line in response.split("\n") if line.strip()]
            return ideas[:5]
        except:
            return [
                f"Top 5 Tipps zu {niche}",
                f"H?ufige Fehler bei {niche}",
                f"Meine Erfahrung mit {niche}",
                f"{niche} f?r Anf?nger",
                f"So startest du mit {niche}"
            ]
    
    def _identify_monetization(self, niche: str) -> List[str]:
        """Identify monetization methods"""
        methods = []
        
        niche_lower = niche.lower()
        
        if any(word in niche_lower for word in ["business", "geld", "money"]):
            methods.extend(["Affiliate Marketing", "Online Kurse", "Coaching"])
        
        if any(word in niche_lower for word in ["tech", "software", "tool"]):
            methods.extend(["Software Affiliate", "Sponsored Content"])
        
        if any(word in niche_lower for word in ["beauty", "fashion", "fitness"]):
            methods.extend(["Product Affiliate", "Brand Deals"])
        
        # Universal methods
        methods.extend(["Ad Revenue", "Merchandise", "Digital Products"])
        
        return list(set(methods))[:5]
    
    def _estimate_revenue(self, profitability_score: float) -> str:
        """Estimate potential monthly revenue"""
        if profitability_score >= 80:
            return "5.000-15.000?"
        elif profitability_score >= 60:
            return "2.000-5.000?"
        elif profitability_score >= 40:
            return "500-2.000?"
        else:
            return "100-500?"
