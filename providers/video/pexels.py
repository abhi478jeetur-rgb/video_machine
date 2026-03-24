"""Pexels video provider for the Video Automation Machine."""

import httpx
from typing import List, Optional
from core.logging_utils import get_logger
from providers.video.base import BaseVideoProvider
from core.types import VideoAsset


logger = get_logger("vam.providers.video")


class PexelsVideoProvider(BaseVideoProvider):
    """Pexels video search provider.
    
    Requires PEXELS_API_KEY in environment variables.
    Get a free key at: https://www.pexels.com/api/
    
    If API key is missing or request fails, returns empty list (no crash).
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = config.get("pexels_api_key")
        self.base_url = "https://api.pexels.com/videos"
        
        if not self.api_key:
            logger.warning("PEXELS_API_KEY not configured - video search will return empty results")
            self.enabled = False
    
    def get_name(self) -> str:
        return "Pexels"
    
    async def search_clips(self, query: str, max_results: int = 5) -> List[VideoAsset]:
        """Search for video clips matching query.
        
        Args:
            query: Search term (e.g., "nature beautiful sunset")
            max_results: Maximum number of clips to return (default 5)
            
        Returns:
            List of VideoAsset objects, or empty list if no results/error
        """
        if not self.api_key:
            logger.warning(f"PEXELS_API_KEY not configured, skipping search for: {query}")
            return []
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "query": query,
                        "per_page": max_results,
                        "orientation": "portrait"
                    },
                    headers={
                        "Authorization": self.api_key
                    },
                    timeout=30.0
                )
                
                if response.status_code == 401:
                    logger.warning("Pexels API key invalid - video search will return empty results")
                    return []
                
                response.raise_for_status()
                data = response.json()
                
                clips = []
                for video_data in data.get("videos", []):
                    # Get fullscreen resolution
                    videos = video_data.get("videos", {})
                    fullscreen = videos.get("fullscreen", {})
                    
                    clips.append(VideoAsset(
                        provider="pexels",
                        provider_id=str(video_data.get("id", "")),
                        url=fullscreen.get("link", ""),
                        width=fullscreen.get("width", 1080),
                        height=fullscreen.get("height", 1920),
                        duration=float(video_data.get("duration", 10)),
                        thumbnail_url=video_data.get("image", ""),
                        metadata={
                            "pexels_id": video_data.get("id", ""),
                            "user": video_data.get("user", {}).get("name", "Unknown")
                        }
                    ))
                
                logger.info(f"Found {len(clips)} clips for query: {query}")
                return clips
                
            except httpx.HTTPError as e:
                logger.warning(f"Pexels API request failed: {e}")
                return []
    
    async def get_clip(self, clip_id: str) -> Optional[VideoAsset]:
        """Get details for a specific clip by ID.
        
        Args:
            clip_id: Pexels video ID
            
        Returns:
            VideoAsset if found, None otherwise
        """
        if not self.api_key:
            return None
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/videos/{clip_id}",
                    headers={"Authorization": self.api_key},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                videos = data.get("videos", {})
                fullscreen = videos.get("fullscreen", {})
                
                return VideoAsset(
                    provider="pexels",
                    provider_id=clip_id,
                    url=fullscreen.get("link", ""),
                    width=fullscreen.get("width", 1080),
                    height=fullscreen.get("height", 1920),
                    duration=float(data.get("duration", 10)),
                    thumbnail_url=data.get("image", ""),
                    metadata={"pexels_id": clip_id}
                )
            except (httpx.HTTPError, KeyError):
                return None
