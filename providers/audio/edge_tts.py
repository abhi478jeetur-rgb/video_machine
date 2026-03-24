"""Edge-TTS provider for the Video Automation Machine."""

import tempfile
import os
from typing import List, Optional
import edge_tts
from core.logging_utils import get_logger
from providers.audio.base import BaseTTSProvider
from core.types import AudioAsset


logger = get_logger("vam.providers.audio")


class EdgeTTSProvider(BaseTTSProvider):
    """Edge-TTS provider using Microsoft's free text-to-speech.
    
    This is the default free TTS provider for the Video Automation Machine.
    No API key required - uses system-installed Edge TTS.
    
    Default voice: en-US-AriaNeural
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.default_voice = config.get("edge_tts_voice", "en-US-AriaNeural")
        self.default_rate = config.get("edge_tts_rate", "+0%")
        self.default_pitch = config.get("edge_tts_pitch", "+0Hz")
        self.temp_dir = config.get("temp_dir", "temp")
        
        # Ensure temp directory exists
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    def get_name(self) -> str:
        return "Edge-TTS"
    
    async def synthesize(self, text: str, voice: Optional[str] = None) -> AudioAsset:
        """Synthesize audio from text using Edge-TTS.
        
        Args:
            text: Script text to convert to speech
            voice: Optional voice identifier (default: en-US-AriaNeural)
            
        Returns:
            AudioAsset with generated audio path and metadata
        """
        voice = voice or self.default_voice
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False,
            dir=self.temp_dir
        ) as tmp:
            output_path = tmp.name
        
        try:
            # Generate audio
            communicate = edge_tts.Communicate(
                text,
                voice,
                rate=self.default_rate,
                pitch=self.default_pitch
            )
            await communicate.save(output_path)
            
            # Estimate duration (approx 15 words per second)
            words = len(text.split())
            duration = max(1.0, words / 15)
            
            logger.info(f"Generated audio: {output_path} ({duration:.1f}s)")
            
            return AudioAsset(
                provider="edge-tts",
                path=output_path,
                duration=duration,
                sample_rate=44100,
                format="mp3",
                voice=voice
            )
            
        except Exception as e:
            logger.warning(f"Edge-TTS synthesis failed: {e}")
            # Return placeholder if synthesis fails
            return AudioAsset(
                provider="edge-tts",
                path="",
                duration=0.0,
                sample_rate=44100,
                format="mp3",
                voice=voice
            )
    
    async def get_voices(self) -> List[str]:
        """Return list of available voices.
        
        Returns:
            List of voice identifiers (ShortName values)
        """
        try:
            voices = await edge_tts.list_voices()
            return [v["ShortName"] for v in voices]
        except Exception as e:
            logger.warning(f"Failed to list voices: {e}")
            return [self.default_voice]
