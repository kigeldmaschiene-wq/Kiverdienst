"""
Video Renderer Agent
FFmpeg-based video assembly
"""
import os
import subprocess
from typing import Dict, List
from app.agents.base_agent import BaseAgent

class VideoRendererAgent(BaseAgent):
    """
    Video assembly using FFmpeg
    
    Steps:
    1. Concatenate character clips
    2. Add audio (voice-over)
    3. Add TikTok-style subtitles
    4. Export 1080x1920 MP4
    """
    
    def __init__(self):
        super().__init__(
            name="VideoRenderer",
            description="FFmpeg-based video assembly"
        )
        self.temp_dir = "/tmp/video_render"
        self.output_dir = "/workspace/kiverdienst_v2/data/videos"
        
        # Create directories
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def execute(self, video_id: int, context: Dict) -> Dict:
        """
        Render video
        
        Args:
            video_id: Video ID
            context: {
                'clips': List[str] - paths to video clips
                'audio_file': str - path to audio file
                'script': Dict - script data (for subtitles)
            }
        """
        with self.measure_time() as timer:
            try:
                clips = context.get('clips', [])
                audio_file = context.get('audio_file')
                script = context.get('script', {})
                
                if not clips:
                    raise ValueError("No video clips provided")
                if not audio_file:
                    raise ValueError("No audio file provided")
                
                # Assemble video
                output_file = self._assemble_video(
                    video_id=video_id,
                    clips=clips,
                    audio_file=audio_file,
                    script=script
                )
                
                # Update database
                await self._update_video(video_id, output_file)
                
                await self.log_action(
                    action="render_video",
                    status="success",
                    message=f"Video rendered: {output_file}",
                    duration_ms=timer.duration_ms,
                    video_id=video_id
                )
                
                return {
                    'success': True,
                    'data': {
                        'video_id': video_id,
                        'output_file': output_file
                    }
                }
                
            except Exception as e:
                self.logger.error(f"Video rendering failed: {e}")
                
                await self.log_action(
                    action="render_video",
                    status="failed",
                    message=str(e),
                    duration_ms=timer.duration_ms,
                    video_id=video_id
                )
                
                return {'success': False, 'error': str(e)}
    
    def _assemble_video(
        self,
        video_id: int,
        clips: List[str],
        audio_file: str,
        script: Dict
    ) -> str:
        """Assemble video with FFmpeg"""
        
        # Temp files
        concat_file = os.path.join(self.temp_dir, f"concat_{video_id}.txt")
        temp_video = os.path.join(self.temp_dir, f"temp_{video_id}.mp4")
        subtitles_file = os.path.join(self.temp_dir, f"subs_{video_id}.srt")
        output_file = os.path.join(self.output_dir, f"video_{video_id}.mp4")
        
        # 1. Create concat file for clips
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        # 2. Concatenate clips
        subprocess.run([
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            temp_video
        ], check=True, capture_output=True)
        
        # 3. Generate subtitles
        self._generate_subtitles(script.get('full_script', ''), subtitles_file)
        
        # 4. Final assembly with audio, subtitles
        subprocess.run([
            'ffmpeg', '-y',
            '-i', temp_video,
            '-i', audio_file,
            '-vf', f"subtitles={subtitles_file}:force_style='FontSize=24,Bold=1,PrimaryColour=&H00FFFF,OutlineColour=&H000000,Outline=2'",
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            '-s', '1080x1920',
            output_file
        ], check=True, capture_output=True)
        
        # Cleanup temp files
        for f in [concat_file, temp_video, subtitles_file]:
            if os.path.exists(f):
                os.remove(f)
        
        return output_file
    
    def _generate_subtitles(self, script: str, output_file: str):
        """
        Generate SRT subtitles
        TikTok-style: word-by-word timing
        """
        words = script.split()
        words_per_second = 2.3
        
        with open(output_file, 'w') as f:
            for i, word in enumerate(words):
                start_time = i / words_per_second
                end_time = (i + 1) / words_per_second
                
                # SRT format
                f.write(f"{i + 1}\n")
                f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                f.write(f"{word}\n\n")
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    async def _update_video(self, video_id: int, output_file: str):
        """Update video in database"""
        from app.database import get_pool
        
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE videos
                SET video_url = $1,
                    status = 'completed',
                    generation_completed_at = NOW()
                WHERE id = $2
            """, output_file, video_id)
