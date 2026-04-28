"""
yt-dlp wrapper module for JDAE.
Handles downloading from SoundCloud URLs with proper logging and error handling.
"""

from typing import Optional, List
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

    def download(self, url: str, max_downloads: Optional[int] = None) -> bool:
        """
        Download content from URL.

        Args:
            url: SoundCloud URL to download from
            max_downloads: Maximum number of files to download (None = unlimited)

        Returns:
            True if download succeeded, False if failed
        """
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

            self.logger.debug(f"Starting download from {url}")
            self.logger.debug(f"Output template: {output_template}")

            with yt_dlp.YoutubeDL(options) as ytdl:
                ytdl.download([url])

            self.logger.info(f"Successfully completed download from {url}")
            return True

        except yt_dlp.utils.DownloadError as e:
            self.logger.error(f"Download error for {url}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error downloading from {url}: {str(e)}")
            return False

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
