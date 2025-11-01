from .base_agent import BaseAgent
from ..utils.azure_tts import AzureTTS
from typing import Dict, Any
import subprocess
import os

class VideoWorkerAgent(BaseAgent):
    """Assemble videos using FFmpeg"""
    
    def __init__(self):
        super().__init__("VideoWorker")
        self.tts = AzureTTS()
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        video_id = task_data.get("video_id")
        script = task_data.get("script", {})
        character_clips = task_data.get("character_clips", [])
        voice_id = task_data.get("voice_id", "de-DE-ConradNeural")
        
        self.logger.info(f"Starting video assembly for video {video_id}")
        
        # 1. Generate voiceover
        full_text = f"{script.get('hook', '')} {script.get('body', '')} {script.get('cta', '')}"
        audio_path = f"/app/data/audio/{video_id}.mp3"
        
        try:
            await self.tts.synthesize(
                full_text,
                voice_id,
                audio_path
            )
        except Exception as e:
            self.logger.error(f"TTS failed: {e}")
            # Continue without audio for now
            audio_path = None
        
        # 2. Assemble video with FFmpeg
        output_path = f"/app/data/videos/{video_id}.mp4"
        
        # Create a simple video (for now, using color background if no clips)
        if not character_clips or not os.path.exists(character_clips[0] if character_clips else ""):
            # Create simple video with text overlay
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", "color=c=black:s=1080x1920:d=35",
                "-vf", f"drawtext=text='{video_id}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            ]
            
            if audio_path and os.path.exists(audio_path):
                cmd.extend(["-i", audio_path, "-shortest"])
            
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                output_path
            ])
        else:
            # Use character clips
            input_clip = character_clips[0]
            cmd = [
                "ffmpeg", "-y",
                "-i", input_clip
            ]
            
            if audio_path and os.path.exists(audio_path):
                cmd.extend(["-i", audio_path])
            
            cmd.extend([
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                output_path
            ])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg failed: {result.stderr}")
            
            self.logger.info(f"Video assembled successfully: {output_path}")
            
            return {
                "video_path": output_path,
                "audio_path": audio_path,
                "success": True
            }
        
        except subprocess.TimeoutExpired:
            raise Exception("Video assembly timed out")
        except Exception as e:
            self.logger.error(f"Video assembly failed: {e}")
            raise
