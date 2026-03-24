# PRD: CLI & Basic UX

**Description**: Command-line interface for running the machine with minimal friction.

**Sections**:
1. **Main Commands**:
   - `vam generate <prompt>` - Generate video from prompt
   - `vam generate --script <file>` - Generate from script file
   - `vam settings` - Open settings UI
   - `vam --help` - Show all options
2. **Interactive Mode**:
   - Prompt for missing API keys if not in config
   - Confirm before rendering
3. **Progress Indicators**:
   - Simple text progress: `[1/5] Generating script...`
   - Final output path clearly displayed
4. **Exit Codes**:
   - 0: Success
   - 1: User error (missing input, invalid config)
   - 2: Runtime error (API failure, render failure)
5. **Logging**:
   - `--verbose` flag for detailed logs
   - Log file written to `logs/vam_YYYYMMDD.log`