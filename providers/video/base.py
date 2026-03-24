"""Base video provider interface for the Video Automation Machine."""

from abc import ABC, abstractmethod
from typing import List
from providers.base import Provider
from core.types import VideoAsset


class BaseVideoProvider(Provider, ABC):
    """Base class for video search providers.
    
    Provides methods for searching video clips based on queries.
    """
    
    @abstractmethod
    async def search_clips(self, query: str, max_results: int = 5) -> List[VideoAsset]:
        """Search for video clips matching query.
        
        Args:
            query: Search term (e.g., "nature beautiful sunset")
            max_results: Maximum number of clips to return (default 5)
            
        Returns:
            List of VideoAsset objects matching the query
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("search_clips must be implemented by subclass")
