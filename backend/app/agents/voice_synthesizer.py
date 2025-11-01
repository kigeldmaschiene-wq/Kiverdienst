from .base_agent import BaseAgent
from ..utils.azure_tts import AzureTTS
from typing import Dict, Any

class VoiceSynthesizerAgent(BaseAgent):
    """Synthesize voice-overs using Azure TTS"""
    
    def __init__(self):
        super().__init__("VoiceSynthesizer")
        self.tts = AzureTTS()
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        script = task_data.get("script", "")
        voice_id = task_data.get("voice_id", "de-DE-ConradNeural")
        output_path = task_data.get("output_path", "/app/data/audio/temp.mp3")
        language = task_data.get("language", "de-DE")
        
        # Prepare full script
        if isinstance(script, dict):
            full_text = f"{script.get('hook', '')} {script.get('body', '')} {script.get('cta', '')}"
        else:
            full_text = str(script)
        
        # Add pauses and emphasis
        enhanced_text = self._enhance_text(full_text)
        
        # Synthesize
        self.logger.info(f"Synthesizing voice with {voice_id}")
        
        try:
            audio_path = await self.tts.synthesize(
                enhanced_text,
                voice_id,
                output_path,
                language
            )
            
            # Get audio duration (estimate)
            word_count = len(full_text.split())
            estimated_duration = word_count * 0.4  # ~150 words per minute
            
            return {
                "audio_path": audio_path,
                "voice_id": voice_id,
                "duration": estimated_duration,
                "word_count": word_count,
                "success": True
            }
        
        except Exception as e:
            self.logger.error(f"Voice synthesis failed: {e}")
            return {
                "audio_path": None,
                "success": False,
                "error": str(e)
            }
    
    def _enhance_text(self, text: str) -> str:
        """Add SSML markup for better speech"""
        # Add pauses at punctuation
        text = text.replace(".", ".<break time='300ms'/>")
        text = text.replace("!", "!<break time='400ms'/>")
        text = text.replace("?", "?<break time='400ms'/>")
        text = text.replace(",", ",<break time='200ms'/>")
        
        # Emphasize key phrases
        emphasis_words = ["wichtig", "krass", "unglaublich", "jetzt", "sofort"]
        for word in emphasis_words:
            text = text.replace(word, f"<emphasis level='strong'>{word}</emphasis>")
        
        return text
