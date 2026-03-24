"""Logging utilities for the Video Automation Machine."""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "vam",
    level: int = logging.INFO,
    log_dir: str = "logs",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Set up a logger with console and optional file handlers.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_dir: Directory for log files
        log_file: Optional specific log file name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file or log_dir:
        if not log_file:
            log_file = f"vam_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Ensure log directory exists
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_path = os.path.join(log_dir, log_file) if log_dir else log_file
        
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "vam") -> logging.Logger:
    """Get a logger instance by name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_error(logger: logging.Logger, message: str, error: Optional[Exception] = None) -> str:
    """Log an error message with optional exception details.
    
    Args:
        logger: Logger instance
        message: Error message
        error: Optional exception to log details
        
    Returns:
        Formatted error string for display
    """
    if error:
        logger.error(f"{message}: {error}")
        return f"{message}: {error}"
    logger.error(message)
    return message


def log_warning(logger: logging.Logger, message: str) -> None:
    """Log a warning message.
    
    Args:
        logger: Logger instance
        message: Warning message
    """
    logger.warning(message)


def log_success(logger: logging.Logger, message: str) -> None:
    """Log a success message.
    
    Args:
        logger: Logger instance
        message: Success message
    """
    logger.info(f"[OK] {message}")


def log_step(logger: logging.Logger, step: int, total: int, message: str) -> None:
    """Log a pipeline step progress.
    
    Args:
        logger: Logger instance
        step: Current step number
        total: Total steps
        message: Step description
    """
    logger.info(f"[{step}/{total}] {message}")
