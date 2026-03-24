# PRD: Reliability & Portability

**Description**: Keep bugs low and setup easy for solo developers and end users.

**Sections**:
1. **Dependency Strategy**:
   - `requirements.txt` with pinned versions
   - Only essential packages: `httpx`, `moviepy`, `python-dotenv`, `edge-tts`
   - No heavy frameworks (Flask optional for web UI)
   - No database - file-based config only
2. **Error Handling**:
   - Try/except at every external call
   - User-friendly error messages (no stack traces)
   - Graceful degradation (skip feature, continue)
   - Retry logic with exponential backoff
3. **Testing**:
   - Unit tests for core engine
   - Provider mock tests
   - CI with GitHub Actions (Windows/Linux)
4. **Packaging**:
   - `pip install .` for installation
   - Optional: `pyinstaller` for standalone executable
5. **Documentation**:
   - `README.md` with 5-minute setup guide
   - `docs/integration-guide.md` for contributors
   - Common errors and fixes