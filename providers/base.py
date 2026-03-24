"""Base provider interfaces for the Video Automation Machine."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class VideoClip:
    """Represents a video clip from a provider."""
    url: str
    width: int
    height: int
    duration: float
    provider: str
    provider_id: str
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AudioFile:
    """Represents generated audio."""
    path: str
    duration: float
    provider: str
    sample_rate: int = 44100
    format: str = "mp3"
    voice: Optional[str] = None


class Provider(ABC):
    """Base provider interface."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = self._check_enabled()
    
    def _check_enabled(self) -> bool:
        """Check if provider is enabled via config."""
        return self.config.get(f"{self.__class__.__name__.lower()}_enabled", True)
    
    @abstractmethod
    def get_name(self) -> str:
        """Return provider name."""
        pass
