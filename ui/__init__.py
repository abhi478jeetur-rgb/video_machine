# Video Automation Machine - UI Package
"""UI package for the Video Automation Machine."""

from .cli import main as cli_main, create_parser
from .web import app, run_server

__all__ = ["cli_main", "create_parser", "app", "run_server"]
