"""Core data types and models for the Video Automation Machine."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ScriptSegment:
    """Represents a segment of the script for a video scene."""
    scene_index: int
    start_time: float
    end_time: float
    duration: float
    description: str  # Scene description for video search
    voiceover: str  # Text to speech
    keywords: List[str] = field(default_factory=list)
    
    @classmethod
    def from_text(cls, scene_index: int, start_time: float, text: str, keywords: List[str] = None) -> "ScriptSegment":
        """Create a segment from text with estimated duration."""
        # Approximate: 15 words per second for speaking
        words = len(text.split())
        duration = max(1.0, words / 15)
        return cls(
            scene_index=scene_index,
            start_time=start_time,
            end_time=start_time + duration,
            duration=duration,
            description=keywords[0] if keywords else text[:50],
            voiceover=text,
            keywords=keywords or []
        )


@dataclass
class VideoAsset:
    """Represents a video clip from a provider."""
    provider: str  # e.g., "pexels"
    provider_id: str
    url: str
    width: int
    height: int
    duration: float
    thumbnail_url: Optional[str] = None
    download_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_downloaded(self) -> bool:
        return self.download_path is not None and self.download_path != ""
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 16 / 9


@dataclass
class AudioAsset:
    """Represents generated audio for the video."""
    provider: str  # e.g., "edge-tts"
    path: str
    duration: float
    sample_rate: int = 44100
    format: str = "mp3"
    voice: Optional[str] = None
    
    @property
    def is_generated(self) -> bool:
        return self.path is not None and self.path != ""


@dataclass
class TimelineItem:
    """Represents an item on the video timeline."""
    start_time: float
    duration: float
    type: str  # "video", "audio", "text"
    asset_id: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineConfig:
    """Configuration for the video generation pipeline."""
    llm_api_key: Optional[str] = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    pexels_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    
    # Pipeline settings
    video_duration: int = 60
    resolution: str = "1080x1920"
    video_provider: str = "pexels"
    audio_provider: str = "edge-tts"
    
    # Paths
    output_dir: str = "output"
    temp_dir: str = "temp"
    logs_dir: str = "logs"
    
    @classmethod
    def from_env(cls) -> "PipelineConfig":
        """Load configuration from environment variables."""
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        return cls(
            llm_api_key=os.getenv("LLM_API_KEY"),
            llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            pexels_api_key=os.getenv("PEXELS_API_KEY"),
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
            video_duration=int(os.getenv("DEFAULT_VIDEO_DURATION", "60")),
            resolution=os.getenv("DEFAULT_RESOLUTION", "1080x1920"),
            video_provider=os.getenv("DEFAULT_VIDEO_PROVIDER", "pexels"),
            audio_provider=os.getenv("DEFAULT_AUDIO_PROVIDER", "edge-tts"),
            output_dir=os.getenv("OUTPUT_DIR", "output"),
            temp_dir=os.getenv("TEMP_DIR", "temp"),
            logs_dir=os.getenv("LOGS_DIR", "logs"),
        )
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of warnings/errors."""
        warnings = []
        errors = []
        
        if not self.llm_api_key:
            errors.append("LLM_API_KEY is required but not configured")
        
        if not self.pexels_api_key:
            warnings.append("PEXELS_API_KEY not configured - video search will fail")
        
        return errors + warnings


@dataclass
class VideoOutput:
    """Result of video generation."""
    output_path: str
    duration: float
    width: int
    height: int
    file_size: int
    created_at: datetime = field(default_factory=datetime.now)
    segments_count: int = 0
    audio_provider: str = ""
    video_provider: str = ""
