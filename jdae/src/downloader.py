"""
yt-dlp wrapper module for JDAE.
Handles downloading from SoundCloud URLs with proper logging and error handling.
"""

from typing import Optional, List, Tuple, Dict, Any
import time
import yt_dlp
import re

from jdae.src.logger import ArchiveLogger


class YTDLLogger:
    """
    Logger for yt_dlp output filtering.
    Only shows relevant download information, suppresses verbose output.
    Also tracks download statistics.
    """

    def __init__(self, archive_logger: ArchiveLogger):
        """
        Initialize yt_dlp logger.

        Args:
            archive_logger: ArchiveLogger instance for logging
        """
        self.archive_logger = archive_logger
        self.print_flag = False
        self.items_attempted = 0
        self.items_already_downloaded = 0

    def debug(self, msg: str) -> None:
        """Print relevant debug messages from yt_dlp."""
        if self.print_flag:
            self.archive_logger.debug(msg)
            self.print_flag = False
        elif msg.startswith("[download]"):
            self.archive_logger.info(msg)
            self.print_flag = True
            # Track statistics from download messages
            self._track_download_stats(msg)

    def warning(self, msg: str) -> None:
        """Print warning messages from yt_dlp."""
        self.archive_logger.warning(f"yt-dlp: {msg}")

    def error(self, msg: str) -> None:
        """Print error messages from yt_dlp."""
        self.archive_logger.error(f"yt-dlp: {msg}")

    def _track_download_stats(self, msg: str) -> None:
        """Extract and track download statistics from yt_dlp messages."""
        # Only track actual files (not playlist/item progress messages)
        # Files have extensions like .aac, .mp3, etc.

        file_extensions = [".aac", ".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus"]
        has_file_ext = any(ext in msg for ext in file_extensions)

        if not has_file_ext:
            return  # Not a file-related message, ignore

        # Track files that are already downloaded (skipped)
        # Pattern: "/path/to/file.aac has already been downloaded"
        if "has already been downloaded" in msg:
            self.items_already_downloaded += 1
            self.items_attempted += 1

        # Track newly downloaded files (file path without "already downloaded")
        # If we see a file path that doesn't say "already downloaded", it's a new download
        elif "/" in msg or "\\" in msg:
            # This is likely a file path being downloaded
            self.items_attempted += 1
            # items_already_downloaded is not incremented (this is a new download)


class ArchiveDownloader:
    """
    Wrapper around yt_dlp for downloading SoundCloud content.
    Handles configuration, error handling, and logging.
    """

    # Output filename template
    OUTPUT_FILE_TEMPLATE = "%(title)s-%(id)s.%(ext)s"

    def __init__(
        self,
        output_dir: str,
        logger: ArchiveLogger,
        oauth: Optional[str] = None,
        hq_enabled: bool = False,
        rate_limit_sec: int = 3,
        listformats: bool = False,
    ):
        """
        Initialize downloader.

        Args:
            output_dir: Base output directory
            logger: ArchiveLogger instance
            oauth: Optional SoundCloud OAuth token for HQ downloads
            hq_enabled: Enable high-quality downloads if oauth provided
            rate_limit_sec: Seconds to wait between requests
            listformats: If True, list available formats instead of downloading
        """
        self.output_dir = output_dir
        self.logger = logger
        self.oauth = oauth
        self.hq_enabled = hq_enabled
        self.rate_limit_sec = rate_limit_sec
        self.listformats = listformats
        self.ytdl_logger = YTDLLogger(logger)

    def _get_ytdl_options(self, output_path: str) -> dict:
        """
        Build yt_dlp options dictionary.

        Args:
            output_path: Full output path template

        Returns:
            Dictionary of yt_dlp options
        """
        options = {
            "format": "ba[acodec!*=opus]",
            "logger": self.ytdl_logger,
            "outtmpl": output_path,
            "listformats": self.listformats,
            "sleep_interval_requests": self.rate_limit_sec,
            "quiet": False,
            "no_warnings": False,
        }

        return options

    def download(
        self, url: str, max_downloads: Optional[int] = None, max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Download content from URL with retry logic.

        Args:
            url: SoundCloud URL to download from
            max_downloads: Maximum number of files to download (None = unlimited)
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary with keys:
                - success: bool - Whether download completed
                - reason: str - Reason for success or failure
                - items_attempted: int - Total items processed
                - items_skipped: int - Items already downloaded
                - items_new: int - Newly downloaded items
        """
        last_error = None
        retry_delays = [2, 5, 10]  # Exponential backoff: 2s, 5s, 10s

        for attempt in range(max_retries):
            try:
                # Set HQ download header if enabled
                if self.hq_enabled and self.oauth:
                    yt_dlp.utils.std_headers["Authorization"] = self.oauth

                # Build output template
                output_template = f"{self.output_dir}/archive/%(playlist)s/{self.OUTPUT_FILE_TEMPLATE}"

                # Create logger to track stats
                ytdl_logger = YTDLLogger(self.logger)

                # Get options
                options = self._get_ytdl_options(output_template)
                options["logger"] = ytdl_logger

                # If max_downloads specified, add it to options
                if max_downloads is not None and max_downloads > 0:
                    options["playlistend"] = max_downloads

                self.logger.debug(
                    f"Starting download from {url} (attempt {attempt + 1}/{max_retries})"
                )
                self.logger.debug(f"Output template: {output_template}")

                with yt_dlp.YoutubeDL(options) as ytdl:
                    ytdl.download([url])

                # Calculate statistics
                items_attempted = ytdl_logger.items_attempted
                items_skipped = ytdl_logger.items_already_downloaded
                items_new = items_attempted - items_skipped

                self.logger.info(
                    f"Successfully completed download from {url} (attempted: {items_attempted}, new: {items_new}, skipped: {items_skipped})"
                )

                return {
                    "success": True,
                    "reason": "Success",
                    "items_attempted": items_attempted,
                    "items_skipped": items_skipped,
                    "items_new": items_new,
                }

            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)
                self.logger.warning(
                    f"Download error for {url} (attempt {attempt + 1}/{max_retries}): {error_msg}"
                )

                # Don't retry certain errors (invalid URL, not found, etc)
                if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                    self.logger.error(f"Permanent error, not retrying: {error_msg}")
                    return {
                        "success": False,
                        "reason": f"Permanent error: {error_msg}",
                        "items_attempted": 0,
                        "items_skipped": 0,
                        "items_new": 0,
                    }

                last_error = error_msg

            except Exception as e:
                error_msg = str(e)
                self.logger.warning(
                    f"Unexpected error downloading from {url} (attempt {attempt + 1}/{max_retries}): {error_msg}"
                )
                last_error = error_msg

            # If not the last attempt, wait before retrying
            if attempt < max_retries - 1:
                wait_time = retry_delays[attempt]
                self.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        # All retries exhausted
        self.logger.error(
            f"Failed to download from {url} after {max_retries} attempts: {last_error}"
        )
        return {
            "success": False,
            "reason": f"Failed after {max_retries} attempts: {last_error}",
            "items_attempted": 0,
            "items_skipped": 0,
            "items_new": 0,
        }

    def extract_info(self, url: str) -> dict:
        """
        Extract information about content at URL without downloading.

        Args:
            url: SoundCloud URL to extract info from

        Returns:
            Dictionary of extracted information
        """
        try:
            self.logger.debug(f"Extracting info from {url}")

            output_template = (
                f"{self.output_dir}/archive/%(playlist)s/{self.OUTPUT_FILE_TEMPLATE}"
            )
            options = self._get_ytdl_options(output_template)

            with yt_dlp.YoutubeDL(options) as ytdl:
                info = ytdl.extract_info(url, download=False)

            self.logger.debug(f"Successfully extracted info from {url}")
            return info

        except Exception as e:
            self.logger.error(f"Failed to extract info from {url}: {str(e)}")
            return {}
