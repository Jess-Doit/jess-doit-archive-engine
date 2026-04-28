"""
State management module for JDAE.
Handles persistence of downloaded URLs and archive state.
"""

import json
import time
from pathlib import Path
from typing import Dict, Set, Optional, Any
from datetime import datetime

from jdae.src.logger import ArchiveLogger


class StateManager:
    """
    Manages archive state persistence.
    Tracks which URLs have been downloaded from which pages to prevent re-downloads.
    """

    def __init__(self, state_file: str, logger: ArchiveLogger):
        """
        Initialize state manager.

        Args:
            state_file: Path to archive_db.json file
            logger: ArchiveLogger instance for logging events
        """
        self.state_file = Path(state_file).expanduser()
        self.logger = logger
        self.state: Dict[str, Dict[str, Any]] = {}

        # Ensure parent directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing state if file exists
        self._load_state()

    def _load_state(self) -> None:
        """Load state from file if it exists."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    self.state = json.load(f)
                self.logger.debug(f"Loaded state from {self.state_file}")
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(
                    f"Failed to load state file ({e}), starting with fresh state"
                )
                self.state = {}
        else:
            self.logger.debug(f"State file not found, creating new: {self.state_file}")
            self.state = {}

    def _save_state(self) -> None:
        """Save current state to file."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
            self.logger.debug(f"Saved state to {self.state_file}")
        except IOError as e:
            self.logger.error(f"Failed to save state file: {e}")

    def _ensure_url_entry(self, url: str) -> None:
        """Ensure URL has an entry in state."""
        if url not in self.state:
            self.state[url] = {
                "downloaded_ids": [],
                "last_checked": None,
                "error_count": 0,
                "created_at": datetime.now().isoformat(),
            }

    def mark_downloaded(self, url: str, file_id: str) -> None:
        """
        Mark a file as downloaded from a URL.

        Args:
            url: The page URL
            file_id: The unique file ID from yt-dlp
        """
        self._ensure_url_entry(url)

        if file_id not in self.state[url]["downloaded_ids"]:
            self.state[url]["downloaded_ids"].append(file_id)
            self._save_state()
            self.logger.debug(f"Marked {file_id} as downloaded from {url}")

    def is_downloaded(self, url: str, file_id: str) -> bool:
        """
        Check if a file has already been downloaded from a URL.

        Args:
            url: The page URL
            file_id: The unique file ID from yt-dlp

        Returns:
            True if file was previously downloaded, False otherwise
        """
        self._ensure_url_entry(url)
        return file_id in self.state[url]["downloaded_ids"]

    def record_check(self, url: str) -> None:
        """
        Record that a URL was checked.

        Args:
            url: The page URL being checked
        """
        self._ensure_url_entry(url)
        self.state[url]["last_checked"] = datetime.now().isoformat()
        self.state[url]["error_count"] = 0  # Reset error count on successful check
        self._save_state()
        self.logger.debug(f"Recorded check for {url}")

    def get_last_checked(self, url: str) -> Optional[str]:
        """
        Get the timestamp of last successful check for a URL.

        Args:
            url: The page URL

        Returns:
            ISO format timestamp or None if never checked
        """
        self._ensure_url_entry(url)
        return self.state[url].get("last_checked")

    def record_error(self, url: str) -> None:
        """
        Record an error for a URL (increments error count).

        Args:
            url: The page URL that had an error
        """
        self._ensure_url_entry(url)
        self.state[url]["error_count"] = self.state[url].get("error_count", 0) + 1
        self._save_state()
        self.logger.debug(
            f"Recorded error for {url} (count: {self.state[url]['error_count']})"
        )

    def reset_errors(self, url: str) -> None:
        """
        Reset error count for a URL.

        Args:
            url: The page URL to reset
        """
        self._ensure_url_entry(url)
        self.state[url]["error_count"] = 0
        self._save_state()

    def get_error_count(self, url: str) -> int:
        """
        Get error count for a URL.

        Args:
            url: The page URL

        Returns:
            Number of consecutive errors for this URL
        """
        self._ensure_url_entry(url)
        return self.state[url].get("error_count", 0)

    def get_downloaded_count(self, url: str) -> int:
        """
        Get count of files downloaded from a URL.

        Args:
            url: The page URL

        Returns:
            Number of files downloaded
        """
        self._ensure_url_entry(url)
        return len(self.state[url]["downloaded_ids"])

    def get_all_urls(self) -> list:
        """Get list of all tracked URLs."""
        return list(self.state.keys())

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current state.

        Returns:
            Dictionary with state statistics
        """
        total_urls = len(self.state)
        total_downloads = sum(len(u["downloaded_ids"]) for u in self.state.values())
        return {
            "total_urls_tracked": total_urls,
            "total_files_downloaded": total_downloads,
            "urls": self.state,
        }
