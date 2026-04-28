"""
Archive orchestrator module for JDAE.
Handles the main archiving workflow and coordinates all components.
"""

import contextlib
import signal
import time
import traceback
from typing import Optional, List

import pause
import pygame

from jdae.src.logger import ArchiveLogger
from jdae.src.state_manager import StateManager
from jdae.src.status_tracker import StatusTracker
from jdae.src.downloader import ArchiveDownloader
from jdae.src.configmanager import ConfigManager
import jdae.src.logos as logos


class Archiver:
    """
    Main orchestrator for the archive engine.
    Coordinates config, logging, state management, and downloading.
    """

    # Title to print before logo
    PRGM_TITLE = "Jess' Archive Engine"

    def __init__(
        self,
        config_manager: ConfigManager,
        logger: ArchiveLogger,
        state_manager: StateManager,
        status_tracker: StatusTracker,
        downloader: ArchiveDownloader,
        skip_intro: bool = False,
        dry_run: bool = False,
    ):
        """
        Initialize archiver.

        Args:
            config_manager: ConfigManager instance
            logger: ArchiveLogger instance
            state_manager: StateManager instance
            status_tracker: StatusTracker instance
            downloader: ArchiveDownloader instance
            skip_intro: If True, skip boot sequence
            dry_run: If True, don't actually download
        """
        self.config = config_manager
        self.logger = logger
        self.state = state_manager
        self.status = status_tracker
        self.downloader = downloader
        self.skip_intro = skip_intro
        self.dry_run = dry_run
        self.shutdown_requested = False

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
        # Raise KeyboardInterrupt to break out of blocking operations like yt_dlp download
        raise KeyboardInterrupt("Graceful shutdown requested")

    def boot_sequence(self, audio_path: str) -> None:
        """
        Print title + logo and play startup audio.

        Args:
            audio_path: Path to audio file to play
        """
        print()
        print(self.PRGM_TITLE)
        print(logos.BOOT_LOGO_80)

        try:
            # Use pygame to play audio across platforms
            with contextlib.redirect_stdout(None):
                pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.get_busy():
                time.sleep(1)
        except Exception as e:
            self.logger.warning(f"Failed to play boot audio: {e}")

        print("\nStarting automated archive client")

    def download_from_url(self, url: str, url_number: int = 1, total_urls: int = 1) -> tuple[int, int]:
        """
        Download all relevant media from URL.

        Args:
            url: SoundCloud URL to download from
            url_number: Current URL number (for status reporting)
            total_urls: Total number of URLs (for status reporting)

        Returns:
            Tuple of (attempted, downloaded) counts
        """
        attempted = 0
        downloaded = 0

        # Update status
        self.status.start_url_check(url, url_number, total_urls)

        try:
            # Get download limits from config
            initial_limit = self.config.get_initial_page_dl_limit()
            archived_limit = self.config.get_archived_page_dl_limit()

            # Determine which limit to use
            last_checked = self.state.get_last_checked(url)
            max_downloads = initial_limit if last_checked is None else archived_limit

            if self.dry_run:
                self.logger.info(f"[DRY-RUN] Would download from: {url}")
                info = self.downloader.extract_info(url)
                if info and "entries" in info:
                    attempted = len(info["entries"])
                    self.logger.info(f"[DRY-RUN] {attempted} items available")
                    self.status.update_download_progress(attempted=attempted)
            else:
                # Perform actual download with retries
                success, reason = self.downloader.download(url, max_downloads=max_downloads if max_downloads > 0 else None)
                
                if success:
                    attempted = 1
                    downloaded = 1
                else:
                    self.status.record_error(reason, url=url)
                    self.logger.warning(f"Failed to download from {url}: {reason}")
                    self.state.record_error(url)
                    self.status.complete_url(url, success=False)
                    return attempted, downloaded

            # Record successful check
            try:
                self.logger.debug(f"Recording check for {url}")
                self.state.record_check(url)
                self.logger.debug(f"Successfully recorded check for {url}")
            except Exception as state_error:
                self.logger.error(f"Failed to record state for {url}: {state_error}")
                self.status.record_error(f"State recording failed: {state_error}", url=url)

            self.status.complete_url(url, success=True)

        except Exception as e:
            error_msg = f"Error occurred on page: {url}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            self.status.record_error(str(e), url=url)
            try:
                self.state.record_error(url)
            except:
                pass
            self.status.complete_url(url, success=False)

        return attempted, downloaded

    def run_once(self) -> None:
        """
        Run archive check once and exit.
        """
        self.logger.info("Starting single archive pass")

        url_list = self.config.get_url_list()
        if not url_list:
            self.logger.warning("No URLs configured in url_list.ini")
            return

        # Filter out empty URLs
        active_urls = [url for url in url_list if url.strip()]
        total_urls = len(active_urls)

        # Print list of pages to user
        print("\nMonitoring the following pages:")
        for url in active_urls:
            print(f" - {url}")

        output_dir = self.config.get_output_dir()
        print(f"\n######\nARCHIVE OUTPUT DIRECTORY: {output_dir}/archive/%(playlist)s/")

        print("\nEngine ready - good luck")
        time.sleep(2)

        total_attempted = 0
        total_downloaded = 0

        # Initialize session tracking
        self.status.start_session(total_urls)

        try:
            # Process each URL
            for url_number, url in enumerate(active_urls, 1):
                if self.shutdown_requested:
                    self.logger.info("Shutdown requested, stopping archive pass")
                    break

                print(f"\n######\n[URL] -- {url}\n")
                attempted, downloaded = self.download_from_url(url, url_number, total_urls)
                total_attempted += attempted
                total_downloaded += downloaded

        except KeyboardInterrupt:
            print("\n\nArchive pass interrupted by user")
            self.logger.info("Archive pass interrupted by user (Ctrl+C)")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            self.logger.error(f"Unexpected error during archive pass: {traceback.format_exc()}")
        finally:
            self.status.complete_session()

        print(f"\n######\nArchive pass completed.")
        self.logger.info(
            f"Archive pass complete: {total_downloaded}/{total_attempted} downloaded"
        )

    def run_continuous(self) -> None:
        """
        Run archive checks continuously in a loop.
        """
        self.logger.info("Starting continuous archive monitoring")

        url_list = self.config.get_url_list()
        if not url_list:
            self.logger.error("No URLs configured in url_list.ini")
            return

        # Filter out empty URLs
        active_urls = [url for url in url_list if url.strip()]
        total_urls = len(active_urls)

        # Print list of pages to user
        print("\nMonitoring the following pages:")
        for url in active_urls:
            print(f" - {url}")

        output_dir = self.config.get_output_dir()
        archive_wait_time = self.config.get_archive_freq()
        print(f"\n######\nARCHIVE OUTPUT DIRECTORY: {output_dir}/archive/%(playlist)s/")

        print("\nEngine ready - good luck")
        time.sleep(2)

        try:
            while True:
                if self.shutdown_requested:
                    break

                # Initialize session tracking
                self.status.start_session(total_urls)

                try:
                    # For every url in the url_list run archiving
                    for url_number, url in enumerate(active_urls, 1):
                        if self.shutdown_requested:
                            break

                        print(f"\n######\n[URL] -- {url}\n")
                        self.download_from_url(url, url_number, total_urls)

                finally:
                    self.status.complete_session()

                print(
                    f"\n######\nArchive pass completed. Will check again in {archive_wait_time}s ({archive_wait_time/3600:.1f}h)"
                )
                self.logger.info(
                    f"Archive pass complete. Next check in {archive_wait_time/3600:.1f} hours"
                )

                # Use pause instead of time.sleep for better handling of system sleep
                pause.seconds(archive_wait_time)

        except KeyboardInterrupt:
            print("\n\nArchive engine stopped by user")
            self.logger.info("Archive engine stopped by user (Ctrl+C)")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            self.logger.error(f"Unexpected error in main loop: {traceback.format_exc()}")

    def run(self, run_once: bool = False) -> None:
        """
        Start the archive engine.

        Args:
            run_once: If True, run once and exit. If False, run continuously.
        """
        # Boot sequence
        if not self.skip_intro:
            try:
                audio_path = self.config.get_boot_audio()
                self.boot_sequence(audio_path)
            except Exception as e:
                self.logger.warning(f"Boot sequence failed: {e}")

        # Run archive
        try:
            if run_once:
                self.run_once()
            else:
                self.run_continuous()
        except Exception as e:
            self.logger.error(f"Archive failed: {traceback.format_exc()}")
            raise
