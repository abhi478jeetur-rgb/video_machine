# PRD: Core Engine

**Description**: The central orchestrator that manages the video generation pipeline from script to final video.

**Sections**:
1. **Overview**: Single pipeline that processes prompts → script → segments → video → final output
2. **Pipeline Stages**:
   - Input validation (prompt or script file)
   - Script generation (LLM provider)
   - Segment planning (split script into ~60s chunks)
   - Video clip sourcing (video provider)
   - Audio generation (TTS provider)
   - Rendering (moviepy-based composition)
3. **Error Handling Strategy**:
   - Graceful degradation (skip optional features)
   - Clear error messages with actionable fixes
   - Retry logic for transient failures
4. **Configuration**:
   - Load from `.env` and config file
   - Per-pipeline override options
5. **Output**:
   - Final video: `output/short_YYYYMMDD_HHMMSS.mp4`
   - Intermediate files in `temp/` (cleaned up after)