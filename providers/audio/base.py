"""Base audio provider interface for the Video Automation Machine."""

from abc import ABC, abstractmethod
from typing import List, Optional
from providers.base import Provider
from core.types import AudioAsset


class BaseTTSProvider(Provider, ABC):
    """Base class for text-to-speech providers.
    
    Provides methods for synthesizing speech from text.
    """
    
    @abstractmethod
    async def synthesize(self, text: str, voice: Optional[str] = None) -> AudioAsset:
        """Synthesize audio from text.
        
        Args:
            text: Script text to convert to speech
            voice: Optional voice identifier (provider-specific)
            
        Returns:
            AudioAsset with generated audio path and metadata
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("synthesize must be implemented by subclass")
    
    @abstractmethod
    async def get_voices(self) -> List[str]:
        """Return list of available voice identifiers.
        
        Returns:
            List of voice identifiers that can be used with synthesize()
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("get_voices must be implemented by subclass")
