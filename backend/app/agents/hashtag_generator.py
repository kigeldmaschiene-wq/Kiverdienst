from .base_agent import BaseAgent
from ..utils.ollama_client import OllamaClient
from typing import Dict, Any, List
import random

class HashtagGeneratorAgent(BaseAgent):
    """Generate viral hashtags for content"""
    
    def __init__(self):
        super().__init__("HashtagGenerator")
        self.ollama = OllamaClient()
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        content = task_data.get("content", "")
        niche = task_data.get("niche", "")
        platform = task_data.get("platform", "tiktok")
        max_hashtags = task_data.get("max_hashtags", 30)
        
        self.logger.info(f"Generating hashtags for {platform} in niche {niche}")
        
        # Generate hashtags using multiple strategies
        trending_tags = await self._get_trending_hashtags(platform, niche)
        niche_tags = await self._get_niche_hashtags(niche)
        content_tags = await self._extract_content_hashtags(content)
        ai_tags = await self._generate_ai_hashtags(content, niche)
        
        # Combine and deduplicate
        all_tags = trending_tags + niche_tags + content_tags + ai_tags
        unique_tags = list(dict.fromkeys(all_tags))  # Preserve order, remove dupes
        
        # Score and rank hashtags
        ranked_tags = self._rank_hashtags(unique_tags, platform, niche)
        
        # Return top hashtags
        final_tags = ranked_tags[:max_hashtags]
        
        return {
            "hashtags": final_tags,
            "count": len(final_tags),
            "platform": platform,
            "strategy_breakdown": {
                "trending": len(trending_tags),
                "niche": len(niche_tags),
                "content": len(content_tags),
                "ai_generated": len(ai_tags)
            }
        }
    
    async def _get_trending_hashtags(self, platform: str, niche: str) -> List[str]:
        """Get currently trending hashtags"""
        # Platform-specific trending tags
        platform_trending = {
            "tiktok": ["fyp", "foryou", "viral", "trending", "foryoupage", "fy"],
            "instagram": ["reels", "reelsinstagram", "reelsviral", "explore", "instagood"],
            "youtube": ["shorts", "youtubeshorts", "viral", "trending"]
        }
        
        base_tags = platform_trending.get(platform, platform_trending["tiktok"])
        
        # Add niche-specific trending
        niche_trending = {
            "KI & Online Business": ["ai", "tech", "business", "entrepreneur", "sidehustle"],
            "Finanzen & Sparen": ["money", "finance", "investing", "wealth", "financialfreedom"],
            "Haustiere & Katzen": ["cats", "catsoftiktok", "cute", "pets", "kitten"],
            "ASMR & Entspannung": ["asmr", "relaxing", "satisfying", "calm", "meditation"]
        }
        
        niche_tags = niche_trending.get(niche, [])
        
        return base_tags + niche_tags
    
    async def _get_niche_hashtags(self, niche: str) -> List[str]:
        """Get niche-specific hashtags"""
        niche_hashtags = {
            "KI & Online Business": [
                "ki", "k?nstlicheintelligenz", "chatgpt", "automation",
                "onlinebusiness", "passiveinkommen", "digitalnomad", "entrepreneur"
            ],
            "Finanzen & Sparen": [
                "sparen", "geldsparen", "finanzen", "investieren", "verm?gensaufbau",
                "spartipps", "geldtipps", "finanziellefreiheit"
            ],
            "Haustiere & Katzen": [
                "katzen", "katze", "katzenleben", "katzenliebe", "catlover",
                "haustiere", "tierliebe", "catsofinstagram"
            ],
            "ASMR & Entspannung": [
                "asmr", "asmrdeutsch", "entspannung", "meditation", "achtsamkeit",
                "stressabbau", "ruhe", "wellness"
            ]
        }
        
        return niche_hashtags.get(niche, [])
    
    async def _extract_content_hashtags(self, content: str) -> List[str]:
        """Extract relevant hashtags from content"""
        if not content:
            return []
        
        # Extract key words from content
        words = content.lower().split()
        
        # Filter to meaningful words (>3 chars, not common words)
        common_words = {"der", "die", "das", "und", "oder", "aber", "f?r", "mit", "ist", "sind"}
        keywords = [
            word.strip(",.!?;:")
            for word in words
            if len(word) > 3 and word not in common_words
        ]
        
        # Convert to hashtags (take first 5)
        return keywords[:5]
    
    async def _generate_ai_hashtags(self, content: str, niche: str) -> List[str]:
        """Use AI to generate creative hashtags"""
        try:
            prompt = f"""Generate 10 viral hashtags for this content in niche '{niche}':

Content: {content[:200]}

Rules:
- One hashtag per line
- No # symbol
- Mix popular and niche-specific
- German and English OK
- Short and memorable"""
            
            response = await self.ollama.generate(prompt, use_large=False, temperature=0.8)
            
            # Parse hashtags
            hashtags = [
                line.strip().strip("#").replace(" ", "")
                for line in response.split("\n")
                if line.strip()
            ]
            
            return hashtags[:10]
        
        except Exception as e:
            self.logger.warning(f"AI hashtag generation failed: {e}")
            return []
    
    def _rank_hashtags(self, hashtags: List[str], platform: str, niche: str) -> List[str]:
        """Rank hashtags by estimated performance"""
        # Score each hashtag
        scored_tags = []
        for tag in hashtags:
            score = self._calculate_hashtag_score(tag, platform, niche)
            scored_tags.append((tag, score))
        
        # Sort by score
        scored_tags.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the hashtags
        return [tag for tag, score in scored_tags]
    
    def _calculate_hashtag_score(self, hashtag: str, platform: str, niche: str) -> float:
        """Calculate hashtag performance score"""
        score = 50.0  # Base score
        
        # Length scoring (shorter is better)
        if len(hashtag) < 10:
            score += 10
        elif len(hashtag) > 20:
            score -= 5
        
        # Platform-specific high performers
        high_performers = {
            "tiktok": ["fyp", "foryou", "viral", "trending"],
            "instagram": ["reels", "explore", "instagood"],
            "youtube": ["shorts", "viral"]
        }
        
        if hashtag in high_performers.get(platform, []):
            score += 20
        
        # Niche relevance (simplified)
        if niche.lower().replace(" ", "") in hashtag.lower():
            score += 15
        
        # Add some randomness for variety
        score += random.uniform(-5, 5)
        
        return score
