"""
Logging utilities for InternVL Evaluation

This module provides centralized logging configuration for the application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union


def setup_logging(
    level: Union[int, str] = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    log_to_console: bool = True
) -> logging.Logger:
    """
    Configure and setup logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logging to file is disabled)
        log_format: Custom log format (if None, uses default format)
        log_to_console: Whether to output logs to console
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # Default log format if not specified
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers to prevent duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        # Ensure parent directory exists
        log_path = Path(log_file)
        if not log_path.parent.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {logging.getLevelName(level)}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__ for the current module)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)