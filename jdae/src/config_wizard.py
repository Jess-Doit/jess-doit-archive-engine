"""
Interactive configuration wizard for JDAE.
Guides users through setup with prompts and validation.
"""

import os
from pathlib import Path
from typing import Optional

from jdae.src.ui import ArchiveUI


class ConfigWizard:
    """
    Interactive wizard for creating JDAE configuration.
    Prompts user for settings and validates inputs.
    """

    def __init__(self):
        """Initialize config wizard."""
        self.ui = ArchiveUI()
        self.config = {}

    def run(self) -> bool:
        """
        Run the interactive configuration wizard.

        Returns:
            True if successful, False if cancelled
        """
        self.ui.print_header("JDAE Configuration Wizard")

        try:
            self._prompt_output_dir()
            self._prompt_archive_frequency()
            self._prompt_hq_downloads()
            self._prompt_oauth_if_hq()
            self._prompt_first_url()

            # Show summary and confirm
            return self._confirm_and_save()

        except KeyboardInterrupt:
            self.ui.print_warning("Setup cancelled by user")
            return False
        except Exception as e:
            self.ui.print_error(f"Setup error: {e}")
            return False

    def _prompt_output_dir(self) -> None:
        """Prompt for output directory."""
        self.ui.print_info("Where should archived files be saved?")
        default = os.path.expanduser("~/JDAE_OUTPUT")
        prompt = f"Output directory [{default}]: "

        while True:
            user_input = input(prompt).strip()
            path = user_input if user_input else default

            # Expand ~ and make absolute
            path = os.path.expanduser(path)

            # Check if writable
            parent = Path(path).parent
            if not parent.exists():
                self.ui.print_warning(f"Parent directory doesn't exist: {parent}")
                if input("Create it? [y/N]: ").lower() == "y":
                    try:
                        parent.mkdir(parents=True, exist_ok=True)
                        self.ui.print_success(f"Created: {parent}")
                    except Exception as e:
                        self.ui.print_error(f"Failed to create directory: {e}")
                        continue
                else:
                    continue

            # Try creating archive subdirectory
            archive_path = Path(path) / "archive"
            try:
                archive_path.mkdir(parents=True, exist_ok=True)
                self.config["output_dir"] = path
                self.ui.print_success(f"Output directory: {path}")
                break
            except Exception as e:
                self.ui.print_error(f"Cannot write to directory: {e}")

    def _prompt_archive_frequency(self) -> None:
        """Prompt for archive check frequency."""
        self.ui.print_info("How often should archives be checked? (in hours)")
        default_hours = 6

        while True:
            user_input = input(f"Archive frequency [{default_hours}h]: ").strip()
            try:
                hours = int(user_input) if user_input else default_hours
                if hours <= 0:
                    self.ui.print_warning("Frequency must be positive")
                    continue
                # Convert to seconds
                self.config["archive_freq_seconds"] = hours * 3600
                self.ui.print_success(f"Archive frequency: every {hours} hour(s)")
                break
            except ValueError:
                self.ui.print_warning("Please enter a valid number")

    def _prompt_hq_downloads(self) -> None:
        """Prompt for HQ download preference."""
        self.ui.print_info("Download high-quality (HQ) files? (requires OAuth)")
        choice = input("Enable HQ downloads? [y/N]: ").lower().strip()
        self.config["hq_enabled"] = choice == "y"
        status = "enabled" if self.config["hq_enabled"] else "disabled"
        self.ui.print_success(f"HQ downloads: {status}")

    def _prompt_oauth_if_hq(self) -> None:
        """Prompt for OAuth token if HQ is enabled."""
        if not self.config.get("hq_enabled"):
            self.config["oauth"] = ""
            return

        self.ui.print_info("Enter your SoundCloud OAuth token (leave blank to skip HQ)")
        oauth = input("OAuth token: ").strip()

        if oauth:
            self.config["oauth"] = oauth
            self.ui.print_success("OAuth token saved")
        else:
            self.config["hq_enabled"] = False
            self.config["oauth"] = ""
            self.ui.print_warning("HQ downloads disabled (no OAuth token provided)")

    def _prompt_first_url(self) -> None:
        """Prompt for first URL to archive."""
        self.ui.print_info("Enter a SoundCloud URL to start archiving (or press Enter to skip)")
        url = input("SoundCloud URL: ").strip()

        self.config["first_url"] = url if url else None

        if url:
            self.ui.print_success(f"First URL: {url}")
        else:
            self.ui.print_info("You can add URLs later in url_list.ini")

    def _confirm_and_save(self) -> bool:
        """Show summary and confirm before saving."""
        self.ui.print_section("Configuration Summary")

        print(f"Output Directory: {self.config['output_dir']}")
        print(f"Archive Frequency: {self.config['archive_freq_seconds'] // 3600} hour(s)")
        print(f"HQ Downloads: {'Enabled' if self.config['hq_enabled'] else 'Disabled'}")
        if self.config.get("first_url"):
            print(f"First URL: {self.config['first_url']}")
        else:
            print("First URL: (none - add later)")

        response = input("\nSave configuration? [Y/n]: ").lower().strip()
        if response and response != "y":
            self.ui.print_warning("Configuration not saved")
            return False

        self._save_configs()
        return True

    def _save_configs(self) -> None:
        """Save configuration to files."""
        config_dir = Path(__file__).parent.parent / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Save gen_config.ini
        gen_config_path = config_dir / "gen_config.ini"
        self._write_gen_config(gen_config_path)

        # Save url_list.ini
        url_list_path = config_dir / "url_list.ini"
        self._write_url_list(url_list_path)

        self.ui.print_success(f"Configuration saved!")
        self.ui.print_info(f"Config files created in: {config_dir}")

    def _write_gen_config(self, path: Path) -> None:
        """Write gen_config.ini file."""
        with open(path, "w") as f:
            f.write("[SETTINGS]\n\n")
            f.write("skip_intro = False\n\n")
            f.write("boot_audio = v1984_sound_studies-3.wav\n\n")
            f.write("initial_page_dl_limit = -1\n\n")
            f.write("archived_page_dl_limit = -1\n\n")
            f.write(f"output_dir = {self.config['output_dir']}\n\n")
            f.write("archive_db_path = ~/JDAE_OUTPUT/archive_db.json\n\n")
            f.write("debug_mode = False\n\n")
            f.write("run_once_mode = False\n\n")
            f.write(f"archive_frequency = {self.config['archive_freq_seconds']}\n\n")
            f.write("oauth = \n\n")
            f.write("high_quality_enable = False\n\n")
            f.write("rate_limit_sec = 3\n\n")
            f.write("listformats = False\n")

    def _write_url_list(self, path: Path) -> None:
        """Write url_list.ini file."""
        with open(path, "w") as f:
            f.write("[urls]\n")
            if self.config.get("first_url"):
                f.write(f"{self.config['first_url']}\n")
            else:
                f.write("# Add SoundCloud URLs here, one per line\n")
                f.write("# Example: https://soundcloud.com/artist-name\n")


def run_setup_wizard() -> bool:
    """Run the configuration wizard."""
    wizard = ConfigWizard()
    return wizard.run()
