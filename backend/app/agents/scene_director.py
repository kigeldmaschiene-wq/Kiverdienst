from .base_agent import BaseAgent
from typing import Dict, Any
import random

class SceneDirectorAgent(BaseAgent):
    """Select and sequence clips based on script"""
    
    def __init__(self):
        super().__init__("SceneDirector")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        script = task_data.get("script", {})
        character_clips = task_data.get("character_clips", [])
        duration = task_data.get("duration", 35)
        
        hook = script.get("hook", "")
        body = script.get("body", "")
        cta = script.get("cta", "")
        
        # Calculate timing
        hook_duration = 3
        body_duration = duration - 8  # Reserve for hook and CTA
        cta_duration = 5
        
        # Select clips for each section
        scenes = []
        
        # Hook scene - energetic, attention-grabbing
        if character_clips:
            hook_clip = self._select_clip(character_clips, "energetic")
            scenes.append({
                "section": "hook",
                "clip_path": hook_clip,
                "duration": hook_duration,
                "text_overlay": hook,
                "effects": ["zoom_in", "text_animation"]
            })
        
        # Body scenes - informative, engaging
        num_body_clips = 3
        body_clip_duration = body_duration / num_body_clips
        
        for i in range(num_body_clips):
            body_clip = self._select_clip(character_clips, "talking")
            scenes.append({
                "section": "body",
                "clip_path": body_clip,
                "duration": body_clip_duration,
                "text_overlay": self._chunk_text(body, i, num_body_clips),
                "effects": ["smooth_transition"]
            })
        
        # CTA scene - clear call to action
        cta_clip = self._select_clip(character_clips, "pointing")
        scenes.append({
            "section": "cta",
            "clip_path": cta_clip,
            "duration": cta_duration,
            "text_overlay": cta,
            "effects": ["highlight", "text_animation", "end_screen"]
        })
        
        self.logger.info(f"Directed {len(scenes)} scenes for video")
        
        return {
            "scenes": scenes,
            "total_duration": duration,
            "clip_count": len(scenes)
        }
    
    def _select_clip(self, clips: list, mood: str) -> str:
        """Select appropriate clip based on mood"""
        if not clips:
            return "/app/data/default.mp4"
        return random.choice(clips)
    
    def _chunk_text(self, text: str, index: int, total: int) -> str:
        """Split text into chunks for multiple clips"""
        words = text.split()
        chunk_size = len(words) // total
        start = index * chunk_size
        end = start + chunk_size if index < total - 1 else len(words)
        return " ".join(words[start:end])
