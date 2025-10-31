from .base_agent import BaseAgent
from typing import Dict, Any, List

class AssetSelectorAgent(BaseAgent):
    """Select stock footage, music, and visual assets"""
    
    def __init__(self):
        super().__init__("AssetSelector")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        niche = task_data.get("niche", "general")
        keywords = task_data.get("keywords", [])
        mood = task_data.get("mood", "energetic")
        
        # Select video assets
        video_assets = await self._select_video_assets(niche, keywords)
        
        # Select music
        music = await self._select_music(mood, niche)
        
        # Select images/overlays
        images = await self._select_images(keywords)
        
        # Select effects
        effects = await self._select_effects(mood)
        
        self.logger.info(f"Selected {len(video_assets)} video assets, music: {music['name']}")
        
        return {
            "video_assets": video_assets,
            "music": music,
            "images": images,
            "effects": effects
        }
    
    async def _select_video_assets(self, niche: str, keywords: List[str]) -> List[Dict]:
        """Select relevant video footage"""
        # Stock footage libraries based on niche
        niche_assets = {
            "KI & Online Business": [
                {"path": "/app/data/assets/tech_1.mp4", "keywords": ["AI", "tech", "computer"]},
                {"path": "/app/data/assets/coding.mp4", "keywords": ["programming", "code"]},
                {"path": "/app/data/assets/workspace.mp4", "keywords": ["office", "work"]}
            ],
            "Finanzen & Sparen": [
                {"path": "/app/data/assets/money_1.mp4", "keywords": ["money", "finance"]},
                {"path": "/app/data/assets/calculator.mp4", "keywords": ["savings", "budget"]},
                {"path": "/app/data/assets/piggybank.mp4", "keywords": ["save", "invest"]}
            ],
            "Haustiere & Katzen": [
                {"path": "/app/data/assets/cat_1.mp4", "keywords": ["cat", "cute", "pet"]},
                {"path": "/app/data/assets/cat_2.mp4", "keywords": ["kitten", "play"]},
                {"path": "/app/data/assets/cat_3.mp4", "keywords": ["funny", "adorable"]}
            ],
            "ASMR & Entspannung": [
                {"path": "/app/data/assets/nature.mp4", "keywords": ["calm", "peaceful"]},
                {"path": "/app/data/assets/water.mp4", "keywords": ["relax", "soothing"]},
                {"path": "/app/data/assets/candle.mp4", "keywords": ["meditation", "zen"]}
            ]
        }
        
        return niche_assets.get(niche, niche_assets["KI & Online Business"])
    
    async def _select_music(self, mood: str, niche: str) -> Dict:
        """Select background music"""
        music_library = {
            "energetic": {
                "name": "Upbeat Energy",
                "path": "/app/data/music/upbeat.mp3",
                "bpm": 128,
                "volume": 0.3
            },
            "calm": {
                "name": "Peaceful Ambience",
                "path": "/app/data/music/calm.mp3",
                "bpm": 80,
                "volume": 0.2
            },
            "motivational": {
                "name": "Rise Up",
                "path": "/app/data/music/motivation.mp3",
                "bpm": 120,
                "volume": 0.35
            }
        }
        
        return music_library.get(mood, music_library["energetic"])
    
    async def _select_images(self, keywords: List[str]) -> List[Dict]:
        """Select overlay images and graphics"""
        return [
            {"path": "/app/data/overlays/arrow.png", "type": "graphic"},
            {"path": "/app/data/overlays/circle.png", "type": "highlight"},
            {"path": "/app/data/overlays/text_bg.png", "type": "background"}
        ]
    
    async def _select_effects(self, mood: str) -> List[str]:
        """Select video effects"""
        effects = {
            "energetic": ["fast_cuts", "zoom_in", "shake", "color_pop"],
            "calm": ["slow_fade", "soft_blur", "gentle_pan"],
            "motivational": ["dramatic_zoom", "light_leak", "cinematic"]
        }
        
        return effects.get(mood, effects["energetic"])
