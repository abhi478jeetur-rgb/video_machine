"""Custom exceptions for the Video Automation Machine."""


class LLMConfigError(Exception):
    """Raised when LLM provider is not properly configured."""
    pass


class VideoProviderError(Exception):
    """Raised when video provider encounters an error."""
    pass


class AudioProviderError(Exception):
    """Raised when audio/TTS provider encounters an error."""
    pass
