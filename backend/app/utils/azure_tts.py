import httpx
import os
import logging

logger = logging.getLogger(__name__)

class AzureTTS:
    """Client for Azure Text-to-Speech API"""
    
    def __init__(self):
        self.key = os.getenv("AZURE_TTS_KEY")
        self.region = os.getenv("AZURE_TTS_REGION", "westeurope")
        self.base_url = f"https://{self.region}.tts.speech.microsoft.com"
        self.timeout = httpx.Timeout(60.0, connect=10.0)
        
        if not self.key:
            logger.warning("AZURE_TTS_KEY not set - voice synthesis will fail")
    
    async def synthesize(
        self, 
        text: str, 
        voice_id: str, 
        output_path: str,
        language: str = "de-DE"
    ):
        """Synthesize speech from text"""
        if not self.key:
            raise ValueError("AZURE_TTS_KEY not configured")
        
        logger.info(f"Synthesizing voice with Azure TTS (voice: {voice_id})...")
        
        # Clean text for SSML
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        ssml = f"""<speak version='1.0' xml:lang='{language}'>
            <voice name='{voice_id}'>{text}</voice>
        </speak>"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cognitiveservices/v1",
                    headers={
                        "Ocp-Apim-Subscription-Key": self.key,
                        "Content-Type": "application/ssml+xml",
                        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
                    },
                    content=ssml
                )
                response.raise_for_status()
                
                # Save audio file
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"TTS saved to {output_path}")
                return output_path
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Azure TTS API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Voice synthesis failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Azure TTS failed: {e}")
            raise Exception(f"Voice synthesis failed: {str(e)}")
    
    def get_available_voices(self):
        """Get list of available German voices"""
        return [
            {"id": "de-DE-ConradNeural", "name": "Conrad", "gender": "Male"},
            {"id": "de-DE-KatjaNeural", "name": "Katja", "gender": "Female"},
            {"id": "de-DE-KillianNeural", "name": "Killian", "gender": "Male"},
            {"id": "de-DE-AmalaNeural", "name": "Amala", "gender": "Female"},
            {"id": "de-DE-BerndNeural", "name": "Bernd", "gender": "Male"},
            {"id": "de-DE-ChristophNeural", "name": "Christoph", "gender": "Male"},
            {"id": "de-DE-ElkeNeural", "name": "Elke", "gender": "Female"},
            {"id": "de-DE-GiselaNeural", "name": "Gisela", "gender": "Female"}
        ]
