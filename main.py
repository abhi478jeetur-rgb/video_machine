# Video Automation Machine
"""Main entry point for the Video Automation Machine."""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.logging_utils import setup_logger, log_error, log_success
from config.settings import load_config, validate_config
from core.types import PipelineConfig
from core.engine import VideoAutomationEngine
from providers.llm import OpenAICompatLLM
from providers.video import PexelsVideoProvider
from providers.audio import EdgeTTSProvider


def show_help():
    """Display help information."""
    print("Video Automation Machine - Generate short videos from prompts or scripts")
    print("")
    print("Usage:")
    print("  python main.py                    - Show pipeline status")
    print("  python main.py generate \"topic\"   - Generate video from prompt")
    print("  python -m ui.cli --help           - Show CLI help")


def load_engine(config) -> VideoAutomationEngine:
    """Load providers and create engine instance.
    
    Args:
        config: PipelineConfig instance
        
    Returns:
        VideoAutomationEngine instance
    """
    llm = OpenAICompatLLM(config.__dict__)
    video = PexelsVideoProvider(config.__dict__)
    tts = EdgeTTSProvider(config.__dict__)
    
    return VideoAutomationEngine(
        config=config,
        llm=llm,
        video=video,
        tts=tts
    )


async def run_generate(prompt: str, config: PipelineConfig) -> bool:
    """Run video generation from prompt.
    
    Args:
        prompt: Video topic/concept
        config: PipelineConfig instance
        
    Returns:
        True if successful, False otherwise
    """
    engine = load_engine(config)
    video_output = await engine.run_from_prompt(prompt)
    
    print(f"\n[SUCCESS] Video generated: {video_output.output_path}")
    print(f"  Duration: {video_output.duration:.1f}s")
    print(f"  Resolution: {video_output.width}x{video_output.height}")
    print(f"  Segments: {video_output.segments_count}")
    
    return True


def main():
    """Main entry point for the Video Automation Machine."""
    logger = setup_logger("vam")
    
    args = sys.argv[1:]
    
    if not args:
        # No arguments - show pipeline status
        logger.info("[START] Video Automation Machine - Starting")
        
        config = load_config()
        is_valid, issues = validate_config(config)
        
        if issues:
            for issue in issues:
                if "ERROR" in issue.upper() or "required" in issue.lower():
                    logger.error(f"[ERROR] {issue}")
                else:
                    logger.warning(f"[WARN] {issue}")
        
        if not is_valid:
            logger.error("Configuration validation failed. Please check your .env file.")
            sys.exit(1)
        
        logger.info("[OK] Configuration loaded successfully")
        
        # Instantiate providers
        logger.info("[INIT] Creating providers...")
        
        llm_provider = OpenAICompatLLM(config.__dict__)
        logger.info(f"[INIT] LLM Provider: {llm_provider.get_name()}")
        
        video_provider = PexelsVideoProvider(config.__dict__)
        logger.info(f"[INIT] Video Provider: {video_provider.get_name()}")
        
        tts_provider = EdgeTTSProvider(config.__dict__)
        logger.info(f"[INIT] TTS Provider: {tts_provider.get_name()}")
        
        # Create engine
        logger.info("[INIT] Creating VideoAutomationEngine...")
        engine = VideoAutomationEngine(
            config=config,
            llm=llm_provider,
            video=video_provider,
            tts=tts_provider
        )
        
        logger.info("[OK] Pipeline ready - engine initialized successfully")
        logger.info("Run `python main.py generate \"your prompt\"` to generate a video")
        return 0
    
    # Handle commands
    command = args[0]
    
    if command in ("--help", "-h"):
        show_help()
        return 0
    
    if command == "generate":
        if len(args) < 2:
            print("Error: No prompt provided")
            print("Usage: python main.py generate \"your topic\"")
            return 1
        
        prompt = " ".join(args[1:])
        
        config = load_config()
        is_valid, issues = validate_config(config)
        
        if issues:
            for issue in issues:
                if "ERROR" in issue.upper() or "required" in issue.lower():
                    logger.error(f"[ERROR] {issue}")
                else:
                    logger.warning(f"[WARN] {issue}")
        
        if not is_valid:
            logger.error("Configuration validation failed. Please check your .env file.")
            return 1
        
        return asyncio.run(run_generate(prompt, config))
    
    print(f"Unknown command: {command}")
    show_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
