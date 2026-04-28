"""
Archive orchestrator module for JDAE.
Handles the main archiving workflow and coordinates all components.
"""

import os
import signal
import time
import traceback
from typing import Optional, List

import pause

# Suppress pygame welcome message before import
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
from tqdm import tqdm

from jdae.src.logger import ArchiveLogger
from jdae.src.state_manager import StateManager
from jdae.src.status_tracker import StatusTracker
from jdae.src.downloader import ArchiveDownloader
from jdae.src.configmanager import ConfigManager
from jdae.src.ui import get_ui
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
        self.ui = get_ui()
        self.skip_intro = skip_intro
        self.dry_run = dry_run
        self.shutdown_requested = False

        # Session tracking for summary reports
        self.session_start_time = None
        self.session_urls_checked = 0
        self.session_new_downloads = 0
        self.session_skipped = 0
        self.session_errors = 0
        self.session_permanently_skipped = 0

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
        self.ui.print_header(self.PRGM_TITLE)
        print(logos.BOOT_LOGO_80)

        try:
            # Use pygame to play audio across platforms
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.get_busy():
                time.sleep(0.1)
        except Exception as e:
            self.logger.warning(f"Failed to play boot audio: {e}")

        self.ui.print_starting_engine(skip_intro=False)

    def download_from_url(
        self, url: str, url_number: int = 1, total_urls: int = 1
    ) -> tuple[int, int]:
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
                    self.ui.print_download_preview(attempted, url)
                    self.status.update_download_progress(attempted=attempted)
            else:
                # Perform actual download with retries
                stats = self.downloader.download(
                    url, max_downloads=max_downloads if max_downloads > 0 else None
                )

                if stats["success"]:
                    attempted = stats["items_attempted"]
                    downloaded = stats["items_new"]
                    skipped = stats["items_skipped"]

                    # Update session tracking
                    self.session_new_downloads += downloaded
                    self.session_skipped += skipped
                else:
                    self.status.record_error(stats["reason"], url=url)
                    self.logger.warning(
                        f"Failed to download from {url}: {stats['reason']}"
                    )
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
                self.status.record_error(
                    f"State recording failed: {state_error}", url=url
                )

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
        self.session_start_time = time.time()

        url_list = self.config.get_url_list()
        if not url_list:
            self.ui.print_warning("No URLs configured in url_list.ini")
            return

        # Filter out empty URLs
        active_urls = [url for url in url_list if url.strip()]
        total_urls = len(active_urls)

        # Show configuration
        output_dir = self.config.get_output_dir()
        archive_freq = self.config.get_archive_freq()
        self.ui.print_config_summary(active_urls, output_dir, archive_freq)

        self.ui.print_info("Engine ready - good luck")
        time.sleep(2)

        total_attempted = 0
        total_downloaded = 0

        # Initialize session tracking
        self.status.start_session(total_urls)
        self.session_urls_checked = 0

        try:
            # Process each URL with progress bar
            with tqdm(
                total=total_urls, desc="Archive Pass Progress", unit="URL"
            ) as pbar:
                for url_number, url in enumerate(active_urls, 1):
                    if self.shutdown_requested:
                        self.logger.info("Shutdown requested, stopping archive pass")
                        break

                    self.ui.print_url_start(url, url_number, total_urls)
                    attempted, downloaded = self.download_from_url(
                        url, url_number, total_urls
                    )
                    total_attempted += attempted
                    total_downloaded += downloaded
                    self.session_urls_checked += 1
                    # Note: session_new_downloads and session_skipped updated in download_from_url()

                    pbar.update(1)
                    pbar.set_description(f"Downloaded: {self.session_new_downloads}")

        except KeyboardInterrupt:
            self.ui.print_shutdown_notice()
            self.logger.info("Archive pass interrupted by user (Ctrl+C)")
        except Exception as e:
            self.ui.print_error(f"Unexpected error: {e}")
            self.logger.error(
                f"Unexpected error during archive pass: {traceback.format_exc()}"
            )
        finally:
            self.status.complete_session()

            # Print summary report
            elapsed_time = (
                time.time() - self.session_start_time if self.session_start_time else 0
            )
            self.ui.print_summary_report(
                urls_checked=self.session_urls_checked,
                new_downloads=self.session_new_downloads,
                skipped=self.session_skipped,
                errors_with_retry=self.session_errors,
                permanently_skipped=self.session_permanently_skipped,
                elapsed_time=elapsed_time,
                next_check_in=0,  # Last pass, no next check
            )

    def run_continuous(self) -> None:
        """
        Run archive checks continuously in a loop.
        """
        self.logger.info("Starting continuous archive monitoring")

        url_list = self.config.get_url_list()
        if not url_list:
            self.ui.print_error("No URLs configured in url_list.ini")
            return

        # Filter out empty URLs
        active_urls = [url for url in url_list if url.strip()]
        total_urls = len(active_urls)

        # Show configuration
        output_dir = self.config.get_output_dir()
        archive_wait_time = self.config.get_archive_freq()
        self.ui.print_config_summary(active_urls, output_dir, archive_wait_time)

        self.ui.print_info("Engine ready - good luck")
        time.sleep(2)

        try:
            while True:
                if self.shutdown_requested:
                    break

                # Reset session counters for new pass
                self.session_start_time = time.time()
                self.session_urls_checked = 0
                self.session_new_downloads = 0
                self.session_skipped = 0
                self.session_errors = 0

                # Initialize session tracking
                self.status.start_session(total_urls)

                try:
                    # For every url in the url_list run archiving with progress bar
                    with tqdm(
                        total=total_urls, desc="Archive Pass Progress", unit="URL"
                    ) as pbar:
                        for url_number, url in enumerate(active_urls, 1):
                            if self.shutdown_requested:
                                break

                            self.ui.print_url_start(url, url_number, total_urls)
                            attempted, downloaded = self.download_from_url(
                                url, url_number, total_urls
                            )
                            self.session_urls_checked += 1
                            # Note: session_new_downloads and session_skipped updated in download_from_url()

                            pbar.update(1)
                            pbar.set_description(
                                f"Downloaded: {self.session_new_downloads}"
                            )

                finally:
                    self.status.complete_session()

                    # Print summary report
                    elapsed_time = time.time() - self.session_start_time
                    self.ui.print_summary_report(
                        urls_checked=self.session_urls_checked,
                        new_downloads=self.session_new_downloads,
                        skipped=self.session_skipped,
                        errors_with_retry=self.session_errors,
                        permanently_skipped=self.session_permanently_skipped,
                        elapsed_time=elapsed_time,
                        next_check_in=archive_wait_time,
                    )

                self.ui.print_waiting_message(archive_wait_time)
                self.logger.info(
                    f"Archive pass complete. Next check in {archive_wait_time/3600:.1f} hours"
                )

                # Use pause instead of time.sleep for better handling of system sleep
                pause.seconds(archive_wait_time)

        except KeyboardInterrupt:
            self.ui.print_shutdown_notice()
            self.logger.info("Archive engine stopped by user (Ctrl+C)")
        except Exception as e:
            self.ui.print_error(f"Unexpected error: {e}")
            self.logger.error(
                f"Unexpected error in main loop: {traceback.format_exc()}"
            )

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
