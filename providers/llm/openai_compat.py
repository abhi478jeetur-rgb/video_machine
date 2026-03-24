"""OpenAI-compatible LLM provider for the Video Automation Machine."""

import json
import httpx
from typing import List, Optional
from core.logging_utils import get_logger
from core.errors import LLMConfigError
from providers.llm.base import BaseLLMProvider
from core.types import ScriptSegment


logger = get_logger("vam.providers.llm")


class OpenAICompatLLM(BaseLLMProvider):
    """OpenAI-compatible LLM provider (NVIDIA, OpenAI, etc.).
    
    This provider works with any OpenAI-compatible API endpoint.
    Configure via environment variables:
    - LLM_API_KEY: Your API key
    - LLM_BASE_URL: Base URL for the endpoint (default: https://api.openai.com/v1)
    - LLM_MODEL: Model name (default: gpt-4o-mini)
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = config.get("llm_api_key")
        self.base_url = config.get("llm_base_url", "https://api.openai.com/v1")
        self.model = config.get("llm_model", "gpt-4o-mini")
        
        if not self.api_key:
            logger.warning("LLM_API_KEY not configured - LLM features will not work")
            self.enabled = False
    
    def get_name(self) -> str:
        return "OpenAICompat"
    
    async def generate_script(self, prompt: str) -> List[ScriptSegment]:
        """Generate a script from prompt.
        
        Args:
            prompt: User's video topic/concept
            
        Returns:
            List of ScriptSegment objects
            
        Raises:
            LLMConfigError: If API key is not configured
        """
        if not self.api_key:
            raise LLMConfigError("LLM_API_KEY not configured in .env file")
        
        system_prompt = self._build_system_prompt()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse JSON response (if valid) or return as single segment
                try:
                    segments_data = json.loads(content)
                    return [ScriptSegment(
                        scene_index=i,
                        start_time=i * 10,
                        end_time=(i + 1) * 10,
                        duration=10.0,
                        description=seg.get("description", ""),
                        voiceover=seg.get("voiceover", ""),
                        keywords=seg.get("keywords", [])
                    ) for i, seg in enumerate(segments_data)]
                except json.JSONDecodeError:
                    # Return single segment with raw text
                    return [ScriptSegment(
                        scene_index=0,
                        start_time=0,
                        end_time=60,
                        duration=60.0,
                        description="Generated video",
                        voiceover=content,
                        keywords=[]
                    )]
                    
            except httpx.HTTPError as e:
                logger.warning(f"LLM API request failed: {e}")
                raise LLMConfigError(f"LLM API request failed: {e}")
    
    async def generate_title(self, text: str) -> str:
        """Generate a title from script text.
        
        Args:
            text: Script text to generate title from
            
        Returns:
            Generated title string
            
        Raises:
            LLMConfigError: If API key is not configured
        """
        if not self.api_key:
            raise LLMConfigError("LLM_API_KEY not configured in .env file")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "Generate a short, engaging title (max 5 words) for this video script."},
                            {"role": "user", "content": f"Title this video:\n\n{text[:500]}"}
                        ],
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
                
            except httpx.HTTPError as e:
                logger.warning(f"LLM title generation failed: {e}")
                # Return fallback title
                return "Generated Video"
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for script generation."""
        return """You are a video scriptwriter for short vertical videos (9:16, ~60 seconds).

Return your response as a JSON array of scene objects. Each scene should have:
- "description": Brief visual description for video search
- "voiceover": The spoken text for this scene
- "keywords": Comma-separated keywords for video search

Example output:
[
  {
    "description": "Beautiful nature scenery",
    "voiceover": "Welcome to this amazing nature documentary.",
    "keywords": "nature, scenery, beautiful"
  }
]"""
    
    async def get_models(self) -> List[str]:
        """Return list of available models (stub)."""
        return [self.model]
