# Video Automation Machine - Providers Audio Package
"""Audio providers package for the Video Automation Machine."""

from .base import BaseTTSProvider
from .edge_tts import EdgeTTSProvider
from .elevenlabs import ElevenLabsTTS

__all__ = ["BaseTTSProvider", "EdgeTTSProvider", "ElevenLabsTTS"]
