# PRD: Provider System (LLM/Video/TTS)

**Description**: Strategy pattern interfaces for pluggable providers with fallback and optional behavior.

**Sections**:
1. **Base Interface Design**:
   - `LLMProvider`: `generate_script(prompt: str) -> str`
   - `VideoProvider`: `search_videos(query: str, count: int) -> list[VideoClip]`
   - `AudioProvider`: `generate_audio(text: str) -> AudioFile`
2. **Provider Registration**:
   - Auto-discover providers from `providers/` subdirs
   - Configurable priority order
3. **Optional vs Required**:
   - Required: Script generation, TTS, video sourcing
   - Optional: ElevenLabs (fallback to Edge-TTS), premium video sources
4. **Error Handling**:
   - Missing API key → skip provider, log warning, try fallback
   - API failure → retry with backoff, then skip to next provider
5. **Implemented Providers**:
   - LLM: OpenAI-compatible (NVIDIA, OpenAI, etc.)
   - Video: Pexels (requires API key, graceful failure if{ missing)
   - Audio: Edge-T