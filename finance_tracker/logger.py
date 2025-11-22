"""
Logging configuration for Finance Tracker

This module sets up application-wide logging with both
file and console output.
"""

import logging
from pathlib import Path


def setup_logger(name="finance_tracker"):
    """
    Configure and return a logger instance.

    Logs are saved to: ~/.finance_tracker_logs/finance.log
    """
    # Create logger
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Create log directory
    log_dir = Path.home() / ".finance_tracker_logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "finance.log"

    # File handler - saves all logs to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler - shows WARNING and above on screen
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # Format: timestamp - level - message
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Create default logger instance
logger = setup_logger()
