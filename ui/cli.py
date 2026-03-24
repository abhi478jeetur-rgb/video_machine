"""CLI interface for the Video Automation Machine.

Usage:
    python -m ui.cli generate --prompt "your topic"
    python -m ui.cli generate --script-file path/to/script.txt
    python -m ui.cli --help
"""

import argparse
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logging_utils import setup_logger
from config.settings import load_config, validate_config
from core.engine import VideoAutomationEngine
from providers.llm import OpenAICompatLLM
from providers.video import PexelsVideoProvider
from providers.audio import EdgeTTSProvider


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="vam",
        description="Video Automation Machine - Generate short videos from prompts or scripts"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a video from a prompt or script file"
    )
    
    generate_group = generate_parser.add_mutually_exclusive_group(required=True)
    generate_group.add_argument(
        "--prompt",
        "-p",
        type=str,
        help="Video topic/concept prompt"
    )
    generate_group.add_argument(
        "--script-file",
        "-s",
        type=str,
        help="Path to a text file containing the script"
    )
    
    generate_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (optional)"
    )
    
    # Settings command
    subparsers.add_parser(
        "settings",
        help="Open settings UI to configure API keys"
    )
    
    return parser


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


async def run_generate(args, config) -> bool:
    """Run video generation based on CLI arguments.
    
    Args:
        args: Parsed CLI arguments
        config: PipelineConfig instance
        
    Returns:
        True if successful, False otherwise
    """
    logger = setup_logger("vam.cli")
    
    logger.info("[CLI] Starting video generation...")
    
    # Load engine
    engine = load_engine(config)
    
    # Determine input source
    if args.prompt:
        logger.info(f"[CLI] Generating from prompt: '{args.prompt}'")
        video_output = await engine.run_from_prompt(args.prompt)
    elif args.script_file:
        script_path = Path(args.script_file)
        if not script_path.exists():
            logger.error(f"[CLI] Script file not found: {args.script_file}")
            return False
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        
        logger.info(f"[CLI] Generating from script file: {args.script_file}")
        video_output = await engine.run_from_script(script)
    else:
        logger.error("[CLI] No input provided")
        return False
    
    # Output results
    logger.info(f"[CLI] Video generated successfully!")
    logger.info(f"[CLI] Output path: {video_output.output_path}")
    logger.info(f"[CLI] Duration: {video_output.duration:.1f}s")
    logger.info(f"[CLI] Resolution: {video_output.width}x{video_output.height}")
    logger.info(f"[CLI] Segments: {video_output.segments_count}")
    logger.info(f"[CLI] Providers: LLM={engine.llm.get_name()}, Video={engine.video.get_name()}, TTS={engine.tts.get_name()}")
    
    return True


async def run_settings() -> None:
    """Run settings UI (placeholder for future implementation)."""
    logger = setup_logger("vam.cli")
    logger.info("[CLI] Settings UI not yet implemented")
    logger.info("[CLI] Edit .env file directly to configure API keys")


async def main(args=None) -> int:
    """Main entry point for the CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Setup logger
    logger = setup_logger("vam.cli")
    
    if not parsed_args.command:
        parser.print_help()
        return 0
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    is_valid, issues = validate_config(config)
    
    if issues:
        for issue in issues:
            if "ERROR" in issue.upper() or "required" in issue.lower():
                logger.error(f"[CONFIG] {issue}")
            else:
                logger.warning(f"[CONFIG] {issue}")
    
    if not is_valid:
        logger.error("[CLI] Configuration validation failed. Please check your .env file.")
        return 1
    
    # Run command
    if parsed_args.command == "generate":
        success = await run_generate(parsed_args, config)
        return 0 if success else 1
    elif parsed_args.command == "settings":
        await run_settings()
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
