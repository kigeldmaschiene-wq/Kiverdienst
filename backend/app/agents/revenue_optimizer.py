from .base_agent import BaseAgent
from typing import Dict, Any, List

class RevenueOptimizerAgent(BaseAgent):
    """Optimize revenue streams and monetization"""
    
    def __init__(self):
        super().__init__("RevenueOptimizer")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        brand_id = task_data.get("brand_id")
        current_revenue = task_data.get("current_revenue", {})
        
        self.logger.info(f"Optimizing revenue for brand {brand_id}")
        
        # Analyze current revenue streams
        stream_analysis = self._analyze_revenue_streams(current_revenue)
        
        # Identify opportunities
        opportunities = self._identify_opportunities(stream_analysis)
        
        # Generate optimization strategy
        strategy = self._generate_strategy(opportunities)
        
        # Calculate projected revenue
        projections = self._calculate_projections(current_revenue, strategy)
        
        return {
            "brand_id": brand_id,
            "current_analysis": stream_analysis,
            "opportunities": opportunities,
            "strategy": strategy,
            "projections": projections
        }
    
    def _analyze_revenue_streams(self, current_revenue: Dict) -> Dict:
        """Analyze current revenue streams"""
        streams = {
            "ad_revenue": current_revenue.get("ad_revenue", 0),
            "affiliate": current_revenue.get("affiliate", 0),
            "products": current_revenue.get("products", 0),
            "sponsorships": current_revenue.get("sponsorships", 0),
            "courses": current_revenue.get("courses", 0)
        }
        
        total = sum(streams.values())
        
        return {
            "streams": streams,
            "total_revenue": total,
            "diversification_score": self._calculate_diversification(streams),
            "primary_stream": max(streams, key=streams.get) if streams else None,
            "underutilized": [k for k, v in streams.items() if v < total * 0.1]
        }
    
    def _calculate_diversification(self, streams: Dict) -> float:
        """Calculate revenue diversification score (0-100)"""
        total = sum(streams.values())
        if total == 0:
            return 0
        
        # Calculate Herfindahl index (lower = more diversified)
        shares = [(v / total) ** 2 for v in streams.values() if v > 0]
        herfindahl = sum(shares)
        
        # Convert to 0-100 score (higher = better diversification)
        diversification = (1 - herfindahl) * 100
        return round(diversification, 1)
    
    def _identify_opportunities(self, analysis: Dict) -> List[Dict]:
        """Identify revenue opportunities"""
        opportunities = []
        
        # Check underutilized streams
        for stream in analysis.get("underutilized", []):
            opportunities.append({
                "type": stream,
                "current_revenue": analysis["streams"].get(stream, 0),
                "potential_increase": "100-300%",
                "effort": "medium",
                "priority": "high"
            })
        
        # Always suggest high-margin opportunities
        opportunities.extend([
            {
                "type": "digital_products",
                "current_revenue": analysis["streams"].get("products", 0),
                "potential_increase": "200-500%",
                "effort": "high",
                "priority": "high",
                "description": "Erstelle hochwertige digitale Produkte (Kurse, Templates, eBooks)"
            },
            {
                "type": "premium_membership",
                "current_revenue": 0,
                "potential_increase": "500?-2000?/Monat",
                "effort": "medium",
                "priority": "medium",
                "description": "Biete exklusive Inhalte f?r zahlende Mitglieder"
            },
            {
                "type": "sponsorships",
                "current_revenue": analysis["streams"].get("sponsorships", 0),
                "potential_increase": "500-5000?/Deal",
                "effort": "low",
                "priority": "high",
                "description": "Akquiriere Brand Deals ab 50k Follower"
            }
        ])
        
        return opportunities
    
    def _generate_strategy(self, opportunities: List[Dict]) -> Dict:
        """Generate revenue optimization strategy"""
        # Prioritize by impact and effort
        high_priority = [o for o in opportunities if o.get("priority") == "high"]
        
        return {
            "phase_1": {
                "timeframe": "Month 1-2",
                "actions": [
                    "Optimiere bestehende Affiliate-Links",
                    "Implementiere strategische Produkt-Placements",
                    "Starte mit Sponsorship-Outreach"
                ],
                "expected_revenue": "500-1500?"
            },
            "phase_2": {
                "timeframe": "Month 3-4",
                "actions": [
                    "Erstelle erstes digitales Produkt",
                    "Baue Email-Liste auf f?r Produktlaunches",
                    "Teste verschiedene Preis-Punkte"
                ],
                "expected_revenue": "1000-3000?"
            },
            "phase_3": {
                "timeframe": "Month 5-6",
                "actions": [
                    "Launch Premium Membership",
                    "Skaliere erfolgreiche Produkte",
                    "Diversifiziere Revenue Streams"
                ],
                "expected_revenue": "2000-5000?"
            }
        }
    
    def _calculate_projections(self, current_revenue: Dict, strategy: Dict) -> Dict:
        """Calculate revenue projections"""
        current_total = sum(current_revenue.values())
        
        return {
            "current_monthly": current_total,
            "month_3_projected": current_total * 1.5,
            "month_6_projected": current_total * 2.5,
            "month_12_projected": current_total * 4.0,
            "growth_rate": "150-300%",
            "confidence": "high" if current_total > 500 else "medium"
        }
