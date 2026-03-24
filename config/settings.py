"""Configuration loader for the Video Automation Machine."""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from core.types import PipelineConfig


def load_config(env_file: str = ".env") -> PipelineConfig:
    """Load configuration from .env file.
    
    Args:
        env_file: Path to .env file
        
    Returns:
        PipelineConfig instance with loaded values
    """
    # Load .env file
    load_dotenv(env_file)
    
    return PipelineConfig.from_env()


def get_env_var(name: str, default: str = "") -> str:
    """Get an environment variable with a default value.
    
    Args:
        name: Environment variable name
        default: Default value if not set
        
    Returns:
        Environment variable value or default
    """
    return os.getenv(name, default)


def get_env_var_bool(name: str, default: bool = False) -> bool:
    """Get a boolean environment variable.
    
    Args:
        name: Environment variable name
        default: Default value if not set
        
    Returns:
        Boolean value
    """
    value = os.getenv(name, str(default))
    return value.lower() in ("true", "1", "yes")


def get_env_var_int(name: str, default: int = 0) -> int:
    """Get an integer environment variable.
    
    Args:
        name: Environment variable name
        default: Default value if not set
        
    Returns:
        Integer value
    """
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def validate_config(config: PipelineConfig) -> tuple[bool, list[str]]:
    """Validate configuration.
    
    Args:
        config: PipelineConfig instance
        
    Returns:
        Tuple of (is_valid, list of warnings/errors)
    """
    errors = []
    warnings = []
    
    if not config.llm_api_key:
        errors.append("LLM_API_KEY is required but not configured")
    
    if not config.pexels_api_key:
        warnings.append("PEXELS_API_KEY not configured - video search will fail")
    
    return len(errors) == 0, warnings + errors
