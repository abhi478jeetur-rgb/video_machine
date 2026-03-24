# PRD: Free Providers & Fallbacks

**Description**: Prioritize free, no-key-required providers for maximum accessibility.

**Sections**:
1. **Default Stack**:
   - LLM: OpenAI-compatible endpoint (requires API key, e.g., NVIDIA)
   - Video: Pexels (requires API key)
   - Audio: Edge-TTS (free, built into Windows/macOS/Linux)
2. **Optional Premium**:
   - ElevenLabs (better voice quality, requires API key)
   - Premium video sources (requires API key)
3. **Fallback Chain**:
   - If primary provider fails → try secondary
   - If all fail → clear error with workaround suggestions
4. **No-Setup Mode**:
   - Edge-TTS works out of the box
   - LLM and Video require API keys with clear error messages
5. **Graceful Degradation**:
   - Missing API key → skip provider, log warning
   - Video search skipped if Pexels key missing → fallback to placeholder