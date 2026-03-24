"""Video Automation Engine for the Video Automation Machine.

This module provides the main orchestration engine for video generation
from prompts or scripts.
"""

import logging
import os
from typing import List, Optional
from pathlib import Path

from core.types import (
    PipelineConfig, VideoOutput, ScriptSegment, VideoAsset, 
    AudioAsset, TimelineItem
)
from providers.llm.base import BaseLLMProvider
from providers.video.base import BaseVideoProvider
from providers.audio.base import BaseTTSProvider
from scripts.render import render_timeline
from core.logging_utils import get_logger


logger = get_logger("vam.engine")


class VideoAutomationEngine:
    """Main orchestration engine for video generation.
    
    The engine coordinates all provider operations to generate a video
    from a prompt or script.
    """
    
    def __init__(
        self,
        config: PipelineConfig,
        llm: BaseLLMProvider,
        video: BaseVideoProvider,
        tts: BaseTTSProvider
    ):
        """Initialize the video automation engine.
        
        Args:
            config: Pipeline configuration with API keys and settings
            llm: LLM provider for script generation
            video: Video provider for clip sourcing
            tts: TTS provider for audio generation
        """
        self.config = config
        self.llm = llm
        self.video = video
        self.tts = tts
        self.logger = logger
        
        self.output_dir = Path(config.output_dir)
        self.temp_dir = Path(config.temp_dir)
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(
            f"Engine initialized: LLM={llm.get_name()}, "
            f"Video={video.get_name()}, TTS={tts.get_name()}"
        )
    
    async def run_from_prompt(self, prompt: str) -> VideoOutput:
        """Generate a video from a text prompt.
        
        Pipeline steps:
        1. Generate script using LLM provider
        2. Split script into segments
        3. Search for video clips matching each segment
        4. Generate audio using TTS provider
        5. Render final video (moviepy)
        
        Args:
            prompt: User's video topic/concept
            
        Returns:
            VideoOutput with final video path and metadata
        """
        self.logger.info("[1/5] Generating script from prompt...")
        
        # Step 1: Generate script
        try:
            segments = await self.llm.generate_script(prompt)
            self.logger.info(f"Generated {len(segments)} script segments")
        except Exception as e:
            self.logger.error(f"LLM script generation failed: {e}")
            segments = []
        
        if not segments:
            self.logger.warning("No script segments generated, using placeholder")
            segments = [ScriptSegment(
                scene_index=0,
                start_time=0,
                end_time=60,
                duration=60.0,
                description="Generated video",
                voiceover="This is a placeholder video since script generation failed.",
                keywords=[]
            )]
        
        # Step 2: Create video segments (already done by LLM)
        self.logger.info(f"[2/5] Created {len(segments)} video segments")
        
        # Step 3: Search for video clips
        self.logger.info("[3/5] Searching for video clips...")
        for i, segment in enumerate(segments):
            try:
                clips = await self.video.search_clips(segment.description, max_results=3)
                if clips:
                    segment.video_asset = clips[0]  # Select best match
                    self.logger.info(f"Segment {i}: Found {len(clips)} clips, selected: {clips[0].provider_id}")
                else:
                    self.logger.warning(f"Segment {i}: No clips found for '{segment.description}'")
            except Exception as e:
                self.logger.warning(f"Segment {i}: Video search failed: {e}")
        
        # Step 4: Generate audio
        self.logger.info("[4/5] Generating audio...")
        for i, segment in enumerate(segments):
            try:
                audio = await self.tts.synthesize(segment.voiceover)
                segment.audio_asset = audio
                self.logger.info(f"Segment {i}: Generated audio ({audio.duration:.1f}s)")
            except Exception as e:
                self.logger.warning(f"Segment {i}: TTS generation failed: {e}")
                # Create placeholder audio
                segment.audio_asset = AudioAsset(
                    provider="edge-tts",
                    path="",
                    duration=segment.duration,
                    sample_rate=44100,
                    format="mp3"
                )
        
        # Step 5: Render final video
        self.logger.info("[5/5] Rendering final video...")
        return await self._render_from_segments(segments)
    
    async def run_from_script(self, script: str) -> VideoOutput:
        """Generate a video from a pre-written script.
        
        Pipeline steps:
        1. Parse script into segments
        2. Search for video clips matching each segment
        3. Generate audio using TTS provider
        4. Render final video (moviepy)
        
        Args:
            script: Full script text to use for video
            
        Returns:
            VideoOutput with final video path and metadata
        """
        self.logger.info("[1/4] Parsing script into segments...")
        
        # Parse script into segments (sentence-based splitting)
        segments = self._parse_script_into_segments(script)
        self.logger.info(f"Parsed script into {len(segments)} segments")
        
        # Step 2: Search for video clips
        self.logger.info("[2/4] Searching for video clips...")
        for i, segment in enumerate(segments):
            try:
                clips = await self.video.search_clips(segment.description, max_results=3)
                if clips:
                    segment.video_asset = clips[0]
                    self.logger.info(f"Segment {i}: Found {len(clips)} clips, selected: {clips[0].provider_id}")
                else:
                    self.logger.warning(f"Segment {i}: No clips found for '{segment.description}'")
            except Exception as e:
                self.logger.warning(f"Segment {i}: Video search failed: {e}")
        
        # Step 3: Generate audio
        self.logger.info("[3/4] Generating audio...")
        for i, segment in enumerate(segments):
            try:
                audio = await self.tts.synthesize(segment.voiceover)
                segment.audio_asset = audio
                self.logger.info(f"Segment {i}: Generated audio ({audio.duration:.1f}s)")
            except Exception as e:
                self.logger.warning(f"Segment {i}: TTS generation failed: {e}")
                segment.audio_asset = AudioAsset(
                    provider="edge-tts",
                    path="",
                    duration=segment.duration,
                    sample_rate=44100,
                    format="mp3"
                )
        
        # Step 4: Render final video
        self.logger.info("[4/4] Rendering final video...")
        return await self._render_from_segments(segments)
    
    async def _render_from_segments(self, segments: List[ScriptSegment]) -> VideoOutput:
        """Render video from prepared segments.
        
        Args:
            segments: List of ScriptSegment with video and audio assets
            
        Returns:
            VideoOutput with final video path
        """
        # Build timeline
        timeline: List[TimelineItem] = []
        current_time = 0.0
        
        for i, segment in enumerate(segments):
            # Add video item
            if hasattr(segment, 'video_asset') and segment.video_asset:
                timeline.append(TimelineItem(
                    start_time=current_time,
                    duration=segment.duration,
                    type="video",
                    asset_id=f"video_{i}",
                    properties={"segment_index": i}
                ))
            
            # Add audio item
            if hasattr(segment, 'audio_asset') and segment.audio_asset and segment.audio_asset.path:
                timeline.append(TimelineItem(
                    start_time=current_time,
                    duration=segment.duration,
                    type="audio",
                    asset_id=f"audio_{i}",
                    properties={"segment_index": i, "voice": segment.audio_asset.voice}
                ))
            
            current_time += segment.duration
        
        self.logger.info(f"Built timeline with {len(timeline)} items")
        
        # Generate output path
        output_filename = f"short_{len(segments)}seg_{current_time:.0f}s.mp4"
        output_path = str(self.output_dir / output_filename)
        
        # Get resolution from config
        try:
            width, height = map(int, self.config.resolution.split('x'))
        except ValueError:
            width, height = 1080, 1920
        
        # Render video
        try:
            video_output = render_timeline(
                timeline=timeline,
                output_path=output_path,
                resolution=(width, height),
                fps=30
            )
            
            # Update output with actual values
            video_output.segments_count = len(segments)
            video_output.audio_provider = self.tts.get_name()
            video_output.video_provider = self.video.get_name()
            
            return video_output
            
        except Exception as e:
            self.logger.error(f"Rendering failed: {e}")
            return VideoOutput(
                output_path=output_path,
                duration=current_time,
                width=width,
                height=height,
                file_size=0,
                segments_count=len(segments),
                audio_provider=self.tts.get_name(),
                video_provider=self.video.get_name()
            )
    
    def _parse_script_into_segments(self, script: str) -> List[ScriptSegment]:
        """Parse script text into segments.
        
        Splits script by sentence or paragraph boundaries.
        
        Args:
            script: Full script text
            
        Returns:
            List of ScriptSegment objects
        """
        import re
        
        # Split by sentence boundaries (period, exclamation, question mark followed by space or newline)
        sentences = re.split(r'(?<=[.!?])\s+', script)
        
        segments = []
        start_time = 0.0
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Create segment from sentence
            segment = ScriptSegment.from_text(
                scene_index=i,
                start_time=start_time,
                text=sentence,
                keywords=[sentence.split()[0] if sentence.split() else "video"]
            )
            
            segments.append(segment)
            start_time = segment.end_time
        
        # If no segments created, use full script as one segment
        if not segments:
            segments = [ScriptSegment(
                scene_index=0,
                start_time=0,
                end_time=60,
                duration=60.0,
                description="Generated video",
                voiceover=script,
                keywords=[]
            )]
        
        return segments
