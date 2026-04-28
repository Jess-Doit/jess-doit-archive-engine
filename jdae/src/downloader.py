"""
yt-dlp wrapper module for JDAE.
Handles downloading from SoundCloud URLs with proper logging and error handling.
"""

from typing import Optional, List, Tuple
import time
import yt_dlp

from jdae.src.logger import ArchiveLogger


class YTDLLogger:
    """
    Logger for yt_dlp output filtering.
    Only shows relevant download information, suppresses verbose output.
    """

    def __init__(self, archive_logger: ArchiveLogger):
        """
        Initialize yt_dlp logger.

        Args:
            archive_logger: ArchiveLogger instance for logging
        """
        self.archive_logger = archive_logger
        self.print_flag = False

    def debug(self, msg: str) -> None:
        """Print relevant debug messages from yt_dlp."""
        if self.print_flag:
            self.archive_logger.debug(msg)
            self.print_flag = False
        elif msg.startswith("[download]"):
            self.archive_logger.info(msg)
            self.print_flag = True

    def warning(self, msg: str) -> None:
        """Print warning messages from yt_dlp."""
        self.archive_logger.warning(f"yt-dlp: {msg}")

    def error(self, msg: str) -> None:
        """Print error messages from yt_dlp."""
        self.archive_logger.error(f"yt-dlp: {msg}")


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

    def download(self, url: str, max_downloads: Optional[int] = None, max_retries: int = 3) -> Tuple[bool, str]:
        """
        Download content from URL with retry logic.

        Args:
            url: SoundCloud URL to download from
            max_downloads: Maximum number of files to download (None = unlimited)
            max_retries: Maximum number of retry attempts

        Returns:
            Tuple of (success: bool, reason: str)
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

                # Get options
                options = self._get_ytdl_options(output_template)

                # If max_downloads specified, add it to options
                if max_downloads is not None and max_downloads > 0:
                    options["playlistend"] = max_downloads

                self.logger.debug(f"Starting download from {url} (attempt {attempt + 1}/{max_retries})")
                self.logger.debug(f"Output template: {output_template}")

                with yt_dlp.YoutubeDL(options) as ytdl:
                    ytdl.download([url])

                self.logger.info(f"Successfully completed download from {url}")
                return True, "Success"

            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)
                self.logger.warning(f"Download error for {url} (attempt {attempt + 1}/{max_retries}): {error_msg}")
                
                # Don't retry certain errors (invalid URL, not found, etc)
                if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                    self.logger.error(f"Permanent error, not retrying: {error_msg}")
                    return False, f"Permanent error: {error_msg}"
                
                last_error = error_msg

            except Exception as e:
                error_msg = str(e)
                self.logger.warning(f"Unexpected error downloading from {url} (attempt {attempt + 1}/{max_retries}): {error_msg}")
                last_error = error_msg

            # If not the last attempt, wait before retrying
            if attempt < max_retries - 1:
                wait_time = retry_delays[attempt]
                self.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        # All retries exhausted
        self.logger.error(f"Failed to download from {url} after {max_retries} attempts: {last_error}")
        return False, f"Failed after {max_retries} attempts: {last_error}"

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

            output_template = f"{self.output_dir}/archive/%(playlist)s/{self.OUTPUT_FILE_TEMPLATE}"
            options = self._get_ytdl_options(output_template)

            with yt_dlp.YoutubeDL(options) as ytdl:
                info = ytdl.extract_info(url, download=False)

            self.logger.debug(f"Successfully extracted info from {url}")
            return info

        except Exception as e:
            self.logger.error(f"Failed to extract info from {url}: {str(e)}")
            return {}
