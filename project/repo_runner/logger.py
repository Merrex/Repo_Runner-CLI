"""
Logging configuration for repo_runner.
"""

import logging
import sys
from typing import Optional


_logger_instance: Optional[logging.Logger] = None


def setup_logger(name: str = 'repo_runner', level: str = None, verbose: bool = False) -> logging.Logger:
    """Setup and configure the logger."""
    global _logger_instance
    
    if _logger_instance is not None:
        return _logger_instance
    
    # Determine log level
    if verbose:
        log_level = logging.DEBUG
    elif level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    else:
        log_level = logging.INFO
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Create formatter
        if verbose:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            formatter = logging.Formatter('%(message)s')
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    _logger_instance = logger
    return logger


def get_logger(name: str = 'repo_runner') -> logging.Logger:
    """Get the configured logger instance."""
    global _logger_instance
    
    if _logger_instance is None:
        return setup_logger(name)
    
    return _logger_instance


def set_log_level(level: str):
    """Set the log level for the logger."""
    logger = get_logger()
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    for handler in logger.handlers:
        handler.setLevel(log_level)