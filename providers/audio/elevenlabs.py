"""ElevenLabs TTS provider stub for the Video Automation Machine.

This is a premium TTS provider that requires an API key.
Implementation is deferred to a future version.

Current status: Stub - raises NotImplementedError for all methods.

Requirements for future implementation:
- ELEVENLABS_API_KEY in environment variables
- Get API key at: https://elevenlabs.io/
"""

from typing import List, Optional
from core.logging_utils import get_logger
from providers.audio.base import BaseTTSProvider
from core.types import AudioAsset


logger = get_logger("vam.providers.audio")


class ElevenLabsTTS(BaseTTSProvider):
    """ElevenLabs premium TTS provider.
    
    This provider is not yet implemented. It is defined as a stub
    to demonstrate the provider interface and allow future expansion.
    
    Requirements:
    - ELEVENLABS_API_KEY in environment variables
    - Get API key at: https://elevenlabs.io/
    
    Future features:
    - Multiple voice options
    - Voice cloning
    - Better quality audio
    - Speech styling controls
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = config.get("elevenlabs_api_key")
        self.default_voice = config.get("elevenlabs_voice_id", "pNInz6obpgDQ4cPm2Paf")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not configured - ElevenLabs provider unavailable")
            self.enabled = False
    
    def get_name(self) -> str:
        return "ElevenLabs"
    
    async def synthesize(self, text: str, voice: Optional[str] = None) -> AudioAsset:
        """Synthesize audio from text using ElevenLabs.
        
        Currently raises NotImplementedError - stub for future implementation.
        """
        raise NotImplementedError(
            "ElevenLabsTTS is not yet implemented. "
            "This is a stub provider. Please use EdgeTTSProvider for now. "
            "To implement: Add ELEVENLABS_API_KEY to .env and implement the API calls."
        )
    
    async def get_voices(self) -> List[str]:
        """Return list of available voices.
        
        Currently raises NotImplementedError - stub for future implementation.
        """
        raise NotImplementedError(
            "ElevenLabsTTS is not yet implemented. "
            "This is a stub provider."
        )
