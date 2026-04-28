"""
Enhanced UI module for JDAE.
Provides colored terminal output and progress tracking with personality.
"""

from colorama import Fore, Back, Style, init
from typing import Optional
import sys

# Initialize colorama for cross-platform color support
init(autoreset=True)


class ArchiveUI:
    """
    Enhanced UI for terminal output with colors and formatting.
    Maintains charm while providing better visual feedback.
    """

    # Color codes
    INFO_COLOR = Fore.CYAN
    SUCCESS_COLOR = Fore.GREEN
    ERROR_COLOR = Fore.RED
    WARNING_COLOR = Fore.YELLOW
    HEADER_COLOR = Fore.MAGENTA
    DIM_COLOR = Fore.WHITE

    # Progress messages for variety
    PROGRESS_MESSAGES = [
        "Diving deep into the archives...",
        "Scanning for new tracks...",
        "Checking for updates...",
        "Archiving in progress...",
        "Working through the collection...",
        "Keeping the archive fresh...",
    ]

    def __init__(self, verbose: bool = False):
        """
        Initialize UI.

        Args:
            verbose: If True, show debug-level detail
        """
        self.verbose = verbose
        self.progress_counter = 0

    def _get_progress_message(self) -> str:
        """Get a progress message with variety."""
        msg = self.PROGRESS_MESSAGES[
            self.progress_counter % len(self.PROGRESS_MESSAGES)
        ]
        self.progress_counter += 1
        return msg

    def print_header(self, text: str) -> None:
        """Print a formatted header."""
        print(f"\n{self.HEADER_COLOR}{'#' * 60}")
        print(f"{text.upper():^60}")
        print(f"{'#' * 60}{Style.RESET_ALL}\n")

    def print_section(self, text: str) -> None:
        """Print a section divider."""
        print(f"\n{self.INFO_COLOR}{'=' * 60}")
        print(f"  {text}")
        print(f"{'=' * 60}{Style.RESET_ALL}\n")

    def print_info(self, text: str) -> None:
        """Print informational message."""
        print(f"{self.INFO_COLOR}[INFO] {text}{Style.RESET_ALL}")

    def print_success(self, text: str) -> None:
        """Print success message."""
        print(f"{self.SUCCESS_COLOR}[OK] {text}{Style.RESET_ALL}")

    def print_warning(self, text: str) -> None:
        """Print warning message."""
        print(f"{self.WARNING_COLOR}[WARN] {text}{Style.RESET_ALL}")

    def print_error(self, text: str) -> None:
        """Print error message."""
        print(f"{self.ERROR_COLOR}[ERROR] {text}{Style.RESET_ALL}")

    def print_progress(self, text: str) -> None:
        """Print progress message with personality."""
        print(f"{self.DIM_COLOR}{text}{Style.RESET_ALL}")

    def print_status(self, text: str) -> None:
        """Print status message."""
        print(f"{self.INFO_COLOR}[STATUS] {text}{Style.RESET_ALL}")

    def print_url_start(self, url: str, number: int, total: int) -> None:
        """Print start of URL processing."""
        self.print_section(f"Processing URL {number}/{total}")
        print(f"{self.DIM_COLOR}  {url}{Style.RESET_ALL}")

    def print_url_complete(self, url: str, success: bool, reason: str = "") -> None:
        """Print completion of URL processing."""
        if success:
            self.print_success(f"URL {url} completed successfully")
        else:
            self.print_error(f"URL {url} failed: {reason}")

    def print_config_summary(self, urls: list, output_dir: str, frequency: int) -> None:
        """Print configuration summary."""
        self.print_header("Configuration")
        print(f"{self.DIM_COLOR}Monitoring {len(urls)} URL(s):{Style.RESET_ALL}")
        for url in urls:
            if url.strip():
                print(f"  • {url}")
        print()
        print(f"{self.DIM_COLOR}Output Directory:{Style.RESET_ALL}")
        print(f"  {output_dir}/archive/")
        print()
        hours = frequency / 3600
        print(f"{self.DIM_COLOR}Check Frequency:{Style.RESET_ALL}")
        print(f"  Every {hours:.1f} hours")

    def print_summary_report(
        self,
        urls_checked: int,
        new_downloads: int,
        skipped: int,
        errors_with_retry: int,
        permanently_skipped: int,
        elapsed_time: float,
        next_check_in: float,
    ) -> None:
        """Print summary report after archive pass."""
        self.print_header("Pass Summary")

        print(f"{self.SUCCESS_COLOR}URLs Checked:{Style.RESET_ALL} {urls_checked}")
        print(f"{self.SUCCESS_COLOR}New Downloads:{Style.RESET_ALL} {new_downloads}")
        print(
            f"{self.WARNING_COLOR}Skipped (Already Archived):{Style.RESET_ALL} {skipped}"
        )
        print(
            f"{self.WARNING_COLOR}Errors (with Retry):{Style.RESET_ALL} {errors_with_retry}"
        )
        print(
            f"{self.ERROR_COLOR}Permanently Skipped:{Style.RESET_ALL} {permanently_skipped}"
        )

        minutes = elapsed_time / 60
        next_hours = next_check_in / 3600
        print()
        print(f"{self.DIM_COLOR}Time Elapsed:{Style.RESET_ALL} {minutes:.1f} minutes")
        print(
            f"{self.INFO_COLOR}Next Check In:{Style.RESET_ALL} {next_hours:.1f} hours"
        )

    def print_download_preview(self, count: int, url: str) -> None:
        """Print dry-run preview of downloads."""
        self.print_progress(f"  [DRY-RUN] Would download {count} items from: {url}")

    def print_retry_notice(self, url: str, attempt: int, max_attempts: int) -> None:
        """Print retry attempt notice."""
        self.print_warning(f"Retry attempt {attempt}/{max_attempts} for {url}")

    def print_connection_error(self, url: str, reason: str) -> None:
        """Print connection error with suggestion."""
        self.print_error(f"Connection error: {reason}")
        self.print_info("Check internet connection and try again")

    def print_invalid_url_error(self, url: str) -> None:
        """Print invalid URL error."""
        self.print_error(f"Invalid URL: {url}")
        self.print_info("Verify the URL is a valid SoundCloud link")

    def print_not_found_error(self, url: str) -> None:
        """Print not found error."""
        self.print_error(f"URL not found: {url}")
        self.print_info("The page may have been deleted or made private")

    def print_oauth_error(self) -> None:
        """Print OAuth token error."""
        self.print_error("OAuth token invalid or expired")
        self.print_info("Check your OAuth token in gen_config.ini")

    def print_starting_engine(self, skip_intro: bool = False) -> None:
        """Print engine startup message."""
        if not skip_intro:
            print()
            print(
                f"{self.SUCCESS_COLOR}Starting automated archive client{Style.RESET_ALL}"
            )
        else:
            print(f"{self.SUCCESS_COLOR}Engine ready - good luck{Style.RESET_ALL}")

    def print_shutdown_notice(self) -> None:
        """Print graceful shutdown notice."""
        print()
        self.print_warning("Archive engine stopped by user")
        print()

    def print_waiting_message(self, wait_time: int) -> None:
        """Print waiting message."""
        hours = wait_time / 3600
        self.print_status(f"Will check again in {wait_time}s ({hours:.1f}h)")

    def print_box(self, text: str, color: str = None) -> None:
        """Print text in a box."""
        if color is None:
            color = self.DIM_COLOR

        width = len(text) + 4
        print(f"{color}┌{'─' * width}┐")
        print(f"│  {text}  │")
        print(f"└{'─' * width}┘{Style.RESET_ALL}")

    def clear_line(self) -> None:
        """Clear current line (for progress updates)."""
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()


# Global UI instance for easy access
_ui_instance: Optional[ArchiveUI] = None


def get_ui(verbose: bool = False) -> ArchiveUI:
    """Get or create the global UI instance."""
    global _ui_instance
    if _ui_instance is None:
        _ui_instance = ArchiveUI(verbose=verbose)
    return _ui_instance
