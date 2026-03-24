# Video Automation Machine - Core Package
"""Core package for the Video Automation Machine."""

from .types import ScriptSegment, VideoAsset, AudioAsset, TimelineItem, PipelineConfig, VideoOutput
from .logging_utils import setup_logger, get_logger
from .errors import LLMConfigError, VideoProviderError, AudioProviderError
from .factory import create_config, create_engine, create_engine_from_env

__all__ = [
    "ScriptSegment",
    "VideoAsset",
    "AudioAsset",
    "TimelineItem",
    "PipelineConfig",
    "VideoOutput",
    "setup_logger",
    "get_logger",
    "LLMConfigError",
    "VideoProviderError",
    "AudioProviderError",
    "create_config",
    "create_engine",
    "create_engine_from_env",
]
