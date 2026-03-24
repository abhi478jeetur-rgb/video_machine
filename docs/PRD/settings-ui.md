# PRD: Simple Settings UI

**Description**: Easy way for users to configure API keys and options without editing files.

**Sections**:
1. **Settings Storage**:
   - Single `.env` file for all config
   - Simple key=value format
2. **UI Options**:
   - **Text UI** (v1): `vam settings` opens simple menu in terminal
   - **Web UI** (v1.1): Tiny Flask server at `http://localhost:8080/settings`
3. **Settings Categories**:
   - API Keys (NVIDIA, Pexels, ElevenLabs, etc.)
   - Default LLM Model/Endpoint
   - Default Video Source
   - Output Settings (resolution, duration)
4. **Validation**:
   - Test API key on save
   - Warn if key is invalid
5. **Portability**:
   - Settings file is human-readable
   - Can be edited manually if needed