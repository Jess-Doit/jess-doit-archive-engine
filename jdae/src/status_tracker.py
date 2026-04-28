"""
Status tracking module for JDAE.
Maintains a status file to show current operations and progress.
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from jdae.src.logger import ArchiveLogger


class StatusTracker:
    """
    Tracks and persists current archive operation status.
    Writes status.json file for monitoring and debugging.
    """

    def __init__(self, status_file: str, logger: ArchiveLogger):
        """
        Initialize status tracker.

        Args:
            status_file: Path to status.json file
            logger: ArchiveLogger instance for logging events
        """
        self.status_file = Path(status_file).expanduser()
        self.logger = logger

        # Ensure parent directory exists
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize status
        self.status: Dict[str, Any] = self._get_default_status()
        self._save_status()

    def _get_default_status(self) -> Dict[str, Any]:
        """Get default status object."""
        return {
            "status": "idle",
            "current_url": None,
            "progress": {
                "urls_checked": 0,
                "urls_total": 0,
                "attempted_downloads": 0,
                "successful_downloads": 0,
                "failed_downloads": 0,
                "skipped_downloads": 0,
            },
            "current_file": None,
            "last_updated": datetime.now().isoformat(),
            "session_start": datetime.now().isoformat(),
            "errors": [],
        }

    def _save_status(self) -> None:
        """Save current status to file."""
        try:
            self.status["last_updated"] = datetime.now().isoformat()
            with open(self.status_file, "w") as f:
                json.dump(self.status, f, indent=2)
            self.logger.debug(f"Status saved to {self.status_file}")
        except Exception as e:
            self.logger.error(f"Failed to save status file: {e}")

    def start_session(self, total_urls: int) -> None:
        """
        Mark the start of an archive session.

        Args:
            total_urls: Total number of URLs to check
        """
        self.status = self._get_default_status()
        self.status["status"] = "running"
        self.status["progress"]["urls_total"] = total_urls
        self._save_status()
        self.logger.info(f"Archive session started - {total_urls} URLs to check")

    def start_url_check(self, url: str, url_number: int, total_urls: int) -> None:
        """
        Mark the start of checking a URL.

        Args:
            url: The URL being checked
            url_number: Current URL number (1-based)
            total_urls: Total number of URLs
        """
        self.status["status"] = "downloading"
        self.status["current_url"] = url
        self.status["progress"]["urls_checked"] = url_number - 1
        self.status["progress"]["urls_total"] = total_urls
        self._save_status()
        self.logger.debug(f"Starting check for URL {url_number}/{total_urls}: {url}")

    def update_download_progress(
        self,
        current_file: Optional[str] = None,
        attempted: int = 0,
        successful: int = 0,
        failed: int = 0,
        skipped: int = 0,
    ) -> None:
        """
        Update download progress for current URL.

        Args:
            current_file: Current file being processed
            attempted: Number of download attempts made
            successful: Number of successful downloads
            failed: Number of failed downloads
            skipped: Number of skipped downloads
        """
        if current_file:
            self.status["current_file"] = current_file

        if attempted > 0:
            self.status["progress"]["attempted_downloads"] = attempted
        if successful > 0:
            self.status["progress"]["successful_downloads"] = successful
        if failed > 0:
            self.status["progress"]["failed_downloads"] = failed
        if skipped > 0:
            self.status["progress"]["skipped_downloads"] = skipped

        self._save_status()

    def complete_url(self, url: str, success: bool = True) -> None:
        """
        Mark a URL as completed.

        Args:
            url: The URL that was completed
            success: Whether the URL was successfully processed
        """
        if success:
            self.status["status"] = "idle"
        else:
            self.status["status"] = "error"

        self.status["current_url"] = None
        self.status["current_file"] = None
        self._save_status()
        self.logger.debug(f"Completed URL check: {url} (success={success})")

    def record_error(self, error_msg: str, url: Optional[str] = None) -> None:
        """
        Record an error that occurred.

        Args:
            error_msg: Error message
            url: Optional URL where error occurred
        """
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "message": error_msg,
            "url": url,
        }
        self.status["errors"].append(error_record)

        # Keep only last 10 errors
        if len(self.status["errors"]) > 10:
            self.status["errors"] = self.status["errors"][-10:]

        self._save_status()
        self.logger.debug(f"Error recorded: {error_msg}")

    def complete_session(self) -> None:
        """Mark the end of an archive session."""
        self.status["status"] = "idle"
        self.status["current_url"] = None
        self.status["current_file"] = None
        self._save_status()
        self.logger.info("Archive session completed")

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return self.status.copy()

    def clear_status(self) -> None:
        """Clear the status file."""
        self.status = self._get_default_status()
        self._save_status()
        self.logger.debug("Status cleared")
