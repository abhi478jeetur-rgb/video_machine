# Video Automation Machine - Provider/Engine Factory
"""Factory functions for creating providers and engine instances.

This module provides shared helper functions that both CLI and Web UI
can use to instantiate providers and the engine consistently.
"""

from core.types import PipelineConfig
from core.engine import VideoAutomationEngine
from providers.llm import OpenAICompatLLM
from providers.video import PexelsVideoProvider
from providers.audio import EdgeTTSProvider


def create_config() -> PipelineConfig:
    """Load configuration from environment variables.
    
    Returns:
        PipelineConfig instance with values from .env file
    """
    from config.settings import load_config
    return load_config()


def create_engine(config: PipelineConfig) -> VideoAutomationEngine:
    """Create a VideoAutomationEngine with default providers.
    
    Args:
        config: PipelineConfig instance
        
    Returns:
        VideoAutomationEngine instance with all providers initialized
    """
    llm = OpenAICompatLLM(config.__dict__)
    video = PexelsVideoProvider(config.__dict__)
    tts = EdgeTTSProvider(config.__dict__)
    
    return VideoAutomationEngine(
        config=config,
        llm=llm,
        video=video,
        tts=tts
    )


def create_engine_from_env() -> VideoAutomationEngine:
    """Create engine with config loaded from environment.
    
    Returns:
        VideoAutomationEngine instance
    """
    config = create_config()
    return create_engine(config)
