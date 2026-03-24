"""Base LLM provider interface for the Video Automation Machine."""

from abc import ABC, abstractmethod
from typing import List
from providers.base import Provider
from core.types import ScriptSegment


class BaseLLMProvider(Provider, ABC):
    """Base class for LLM providers (Strategy pattern).
    
    Provides methods for generating video scripts and titles from prompts.
    """
    
    @abstractmethod
    async def generate_script(self, prompt: str) -> List[ScriptSegment]:
        """Generate a script from prompt as a list of segments.
        
        Args:
            prompt: User's video topic/concept
            
        Returns:
            List of ScriptSegment objects representing the video script
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("generate_script must be implemented by subclass")
    
    @abstractmethod
    async def generate_title(self, text: str) -> str:
        """Generate a title from script text.
        
        Args:
            text: Script text to generate title from
            
        Returns:
            Generated title string
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("generate_title must be implemented by subclass")
