"""
Structured logging module for JDAE.
Provides logging to both console and file with appropriate formatting.
"""

import logging
import os
from pathlib import Path
from typing import Optional


class ArchiveLogger:
    """
    Handles all logging for the archive engine.
    Logs to both console and file with structured formatting.
    """

    def __init__(self, output_dir: str, debug: bool = False):
        """
        Initialize logger with console and file output.

        Args:
            output_dir: Base directory for output (log file will be in output_dir/archive.log)
            debug: If True, set log level to DEBUG, otherwise INFO
        """
        self.debug_mode = debug
        self.output_dir = Path(output_dir).expanduser()
        self.log_file = self.output_dir / "archive.log"

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger("jdae")
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)

        # Remove any existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create formatters
        detailed_format = "%(asctime)s - %(levelname)-8s - %(message)s"
        console_format = "%(levelname)-8s - %(message)s"

        # File handler (always detailed)
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(detailed_format))
        self.logger.addHandler(file_handler)

        # Console handler (less verbose)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        console_handler.setFormatter(logging.Formatter(console_format))
        self.logger.addHandler(console_handler)

    def debug(self, msg: str) -> None:
        """Log a debug message (only shown if debug mode enabled)."""
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        """Log an info message."""
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        """Log a warning message."""
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        """Log an error message."""
        self.logger.error(msg)

    def critical(self, msg: str) -> None:
        """Log a critical message."""
        self.logger.critical(msg)

    def get_log_file_path(self) -> str:
        """Return the path to the log file."""
        return str(self.log_file)
