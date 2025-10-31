from .base_agent import BaseAgent
from typing import Dict, Any
import random

class AffiliateTrackerAgent(BaseAgent):
    """Track and optimize affiliate performance"""
    
    def __init__(self):
        super().__init__("AffiliateTracker")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        brand_id = task_data.get("brand_id")
        time_period = task_data.get("time_period", "30_days")
        
        self.logger.info(f"Tracking affiliate performance for brand {brand_id}")
        
        # Collect affiliate metrics
        metrics = await self._collect_metrics(brand_id, time_period)
        
        # Analyze performance
        analysis = self._analyze_performance(metrics)
        
        # Identify top performers
        top_performers = self._identify_top_performers(metrics)
        
        # Generate optimization suggestions
        optimizations = self._generate_optimizations(analysis)
        
        return {
            "brand_id": brand_id,
            "time_period": time_period,
            "metrics": metrics,
            "analysis": analysis,
            "top_performers": top_performers,
            "optimizations": optimizations
        }
    
    async def _collect_metrics(self, brand_id: int, time_period: str) -> Dict:
        """Collect affiliate metrics"""
        # In production: Query database for actual metrics
        
        return {
            "total_clicks": random.randint(500, 5000),
            "total_conversions": random.randint(10, 200),
            "total_revenue": random.uniform(100, 5000),
            "total_commission": random.uniform(20, 1000),
            "active_links": random.randint(5, 20),
            "click_through_rate": random.uniform(0.02, 0.10),
            "conversion_rate": random.uniform(0.01, 0.05),
            "average_order_value": random.uniform(20, 150),
            "roi": random.uniform(2.0, 8.0)
        }
    
    def _analyze_performance(self, metrics: Dict) -> Dict:
        """Analyze affiliate performance"""
        clicks = metrics["total_clicks"]
        conversions = metrics["total_conversions"]
        revenue = metrics["total_revenue"]
        commission = metrics["total_commission"]
        
        return {
            "performance_rating": self._calculate_rating(metrics),
            "conversion_quality": "high" if metrics["conversion_rate"] > 0.03 else "medium",
            "revenue_per_click": revenue / clicks if clicks else 0,
            "commission_rate": (commission / revenue * 100) if revenue else 0,
            "trending": random.choice(["up", "stable", "down"])
        }
    
    def _identify_top_performers(self, metrics: Dict) -> list:
        """Identify top performing affiliate products"""
        # Simulated top products
        return [
            {
                "product_name": "KI Masterclass",
                "clicks": random.randint(200, 1000),
                "conversions": random.randint(10, 50),
                "revenue": random.uniform(500, 2000),
                "commission": random.uniform(100, 400)
            },
            {
                "product_name": "Online Business Bundle",
                "clicks": random.randint(150, 800),
                "conversions": random.randint(8, 40),
                "revenue": random.uniform(400, 1500),
                "commission": random.uniform(80, 300)
            },
            {
                "product_name": "Passive Income Guide",
                "clicks": random.randint(100, 600),
                "conversions": random.randint(5, 30),
                "revenue": random.uniform(200, 800),
                "commission": random.uniform(40, 160)
            }
        ]
    
    def _calculate_rating(self, metrics: Dict) -> str:
        """Calculate performance rating"""
        score = 0
        
        # CTR score
        if metrics["click_through_rate"] > 0.05:
            score += 25
        elif metrics["click_through_rate"] > 0.03:
            score += 15
        
        # Conversion rate score
        if metrics["conversion_rate"] > 0.03:
            score += 25
        elif metrics["conversion_rate"] > 0.02:
            score += 15
        
        # ROI score
        if metrics["roi"] > 5:
            score += 30
        elif metrics["roi"] > 3:
            score += 20
        
        # Revenue score
        if metrics["total_revenue"] > 2000:
            score += 20
        elif metrics["total_revenue"] > 500:
            score += 10
        
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "average"
        else:
            return "needs_improvement"
    
    def _generate_optimizations(self, analysis: Dict) -> list:
        """Generate optimization suggestions"""
        optimizations = []
        
        if analysis["performance_rating"] in ["average", "needs_improvement"]:
            optimizations.extend([
                "Teste verschiedene Produktplatzierungen im Content",
                "Optimiere Call-to-Action Texte",
                "F?ge mehr Social Proof hinzu",
                "Erstelle produkt-spezifische Landing Pages"
            ])
        
        if analysis["conversion_quality"] == "medium":
            optimizations.extend([
                "Verbessere Produkt-Targeting nach Audience",
                "F?ge Rabatt-Codes hinzu",
                "Implementiere Urgency-Elemente"
            ])
        
        optimizations.append("A/B teste verschiedene Affiliate-Produkte")
        
        return optimizations
