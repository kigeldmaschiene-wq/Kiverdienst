from .base_agent import BaseAgent
from typing import Dict, Any, List
import random

class QualityCheckerAgent(BaseAgent):
    """Validate video quality before publishing"""
    
    def __init__(self):
        super().__init__("QualityChecker")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        video_path = task_data.get("video_path")
        script = task_data.get("script", {})
        brand_standards = task_data.get("brand_standards", {})
        
        if not video_path:
            raise ValueError("video_path required")
        
        self.logger.info(f"Checking quality for video: {video_path}")
        
        # Run all quality checks
        checks = {
            "technical": await self._check_technical_quality(video_path),
            "content": await self._check_content_quality(script),
            "compliance": await self._check_compliance(script),
            "brand": await self._check_brand_consistency(script, brand_standards),
            "engagement": await self._predict_engagement(script)
        }
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(checks)
        
        # Determine if video passes
        passed = overall_score >= 70
        
        # Generate recommendations
        recommendations = self._generate_recommendations(checks)
        
        return {
            "passed": passed,
            "overall_score": overall_score,
            "checks": checks,
            "recommendations": recommendations,
            "video_path": video_path
        }
    
    async def _check_technical_quality(self, video_path: str) -> Dict:
        """Check technical aspects"""
        # In production: Use FFprobe/OpenCV for actual checks
        
        return {
            "score": random.uniform(75, 95),
            "resolution": "1080x1920",
            "fps": 30,
            "bitrate": "4000 kbps",
            "audio_quality": "128 kbps",
            "duration": random.uniform(25, 40),
            "file_size": f"{random.uniform(5, 20):.1f} MB",
            "issues": []
        }
    
    async def _check_content_quality(self, script: Dict) -> Dict:
        """Check content quality"""
        issues = []
        score = 100
        
        hook = script.get("hook", "")
        body = script.get("body", "")
        cta = script.get("cta", "")
        
        # Check hook
        if not hook or len(hook) < 10:
            issues.append("Hook zu kurz oder fehlend")
            score -= 20
        
        # Check body
        if not body or len(body) < 50:
            issues.append("Body-Content zu kurz")
            score -= 15
        
        # Check CTA
        if not cta:
            issues.append("Call-to-Action fehlt")
            score -= 10
        
        # Check for filler words
        filler_words = ["?hm", "also", "halt", "eigentlich"]
        text = f"{hook} {body} {cta}".lower()
        found_fillers = [w for w in filler_words if w in text]
        if found_fillers:
            issues.append(f"F?llw?rter gefunden: {', '.join(found_fillers)}")
            score -= 5
        
        return {
            "score": max(score, 0),
            "hook_length": len(hook),
            "body_length": len(body),
            "has_cta": bool(cta),
            "issues": issues
        }
    
    async def _check_compliance(self, script: Dict) -> Dict:
        """Check for policy violations"""
        issues = []
        score = 100
        
        text = " ".join([
            script.get("hook", ""),
            script.get("body", ""),
            script.get("cta", "")
        ]).lower()
        
        # Check for prohibited content
        prohibited_words = ["sex", "nackt", "drogen", "gewalt", "tod"]
        found = [w for w in prohibited_words if w in text]
        if found:
            issues.append(f"Unzul?ssige Begriffe: {', '.join(found)}")
            score -= 30
        
        # Check for spam indicators
        spam_words = ["kaufe jetzt", "klicke hier", "garantiert", "gratis geld"]
        found_spam = [w for w in spam_words if w in text]
        if found_spam:
            issues.append("M?gliche Spam-Indikatoren gefunden")
            score -= 15
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            issues.append("Zu viele Gro?buchstaben")
            score -= 10
        
        return {
            "score": max(score, 0),
            "compliant": len(issues) == 0,
            "issues": issues
        }
    
    async def _check_brand_consistency(self, script: Dict, standards: Dict) -> Dict:
        """Check brand voice consistency"""
        score = 90  # Assume good by default
        issues = []
        
        # Check tone
        expected_tone = standards.get("tone", "professional")
        # In production: Use NLP to analyze tone
        
        # Check keywords
        required_keywords = standards.get("keywords", [])
        text = " ".join([
            script.get("hook", ""),
            script.get("body", ""),
            script.get("cta", "")
        ]).lower()
        
        missing_keywords = [kw for kw in required_keywords if kw.lower() not in text]
        if missing_keywords:
            issues.append(f"Fehlende Schl?sselw?rter: {', '.join(missing_keywords)}")
            score -= 10
        
        return {
            "score": score,
            "tone_match": True,
            "issues": issues
        }
    
    async def _predict_engagement(self, script: Dict) -> Dict:
        """Predict engagement potential"""
        # Simplified engagement prediction
        score = random.uniform(60, 95)
        
        factors = {
            "hook_strength": random.uniform(70, 95),
            "content_value": random.uniform(65, 90),
            "cta_clarity": random.uniform(60, 95)
        }
        
        return {
            "score": score,
            "predicted_views": random.randint(1000, 50000),
            "predicted_engagement_rate": random.uniform(0.05, 0.15),
            "factors": factors
        }
    
    def _calculate_overall_score(self, checks: Dict) -> float:
        """Calculate weighted overall score"""
        weights = {
            "technical": 0.20,
            "content": 0.30,
            "compliance": 0.25,
            "brand": 0.15,
            "engagement": 0.10
        }
        
        total_score = sum(
            checks[key]["score"] * weights[key]
            for key in weights
        )
        
        return round(total_score, 1)
    
    def _generate_recommendations(self, checks: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for check_name, check_data in checks.items():
            if check_data["score"] < 80:
                if check_data.get("issues"):
                    recommendations.extend(check_data["issues"])
        
        if not recommendations:
            recommendations.append("Video erf?llt alle Qualit?tsstandards!")
        
        return recommendations
