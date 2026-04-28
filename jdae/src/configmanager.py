import configparser
import importlib.resources as import_resources
from pathlib import Path
from typing import Optional


class ConfigManager(object):
    """
    Simplifies reading settings from user controlled config files
    """

    # Config file names
    GEN_CONFIG = "gen_config.ini"
    URL_CONFIG = "url_list.ini"

    # Resource base paths
    AUDIO_RESOURCE = "jdae.sounds"
    CONFIG_RESOURCE = "jdae.config"

    # General config sections
    GC_SETTINGS = "SETTINGS"

    def __init__(self, custom_config_path: Optional[str] = None):
        """
        ConfigManager constructor

        Args:
            custom_config_path: Optional path to custom gen_config.ini file
        """
        # Get paths to ini config files
        if custom_config_path:
            self.gen_config_path = str(Path(custom_config_path).expanduser())
        else:
            self.gen_config_path = self._get_config_path(self.GEN_CONFIG)

        self.url_config_path = self._get_config_path(self.URL_CONFIG)

        # Create config parser and parse general config file
        self.parser = configparser.ConfigParser()
        self.parser.read(self.gen_config_path)

        # Validate that required config exists
        self._validate_config()

    def _get_config_path(self, filename):
        """
        Get path to config file in package
        """
        return self._get_path(self.CONFIG_RESOURCE, filename)

    def _get_audio_path(self, filename):
        """
        Get path of audio file in package
        """
        return self._get_path(self.AUDIO_RESOURCE, filename)

    def _get_path(self, resource, filename):
        """
        Get path of resource
        """
        try:
            with import_resources.path(resource, filename) as p:
                config_path = p.as_posix()
            return config_path
        except:
            return ""

    def _parse_bool(self, value: str) -> bool:
        """
        Parse string to boolean value consistently.

        Args:
            value: String value to parse

        Returns:
            Boolean value
        """
        return str(value).lower() in ["true", "yes", "1", "on"]

    def _validate_config(self) -> None:
        """
        Validate that required config keys exist in the config file.
        Raises KeyError if required keys are missing.
        """
        required_keys = [
            "skip_intro",
            "boot_audio",
            "output_dir",
            "archive_frequency",
            "oauth",
            "high_quality_enable",
            "rate_limit_sec",
            "listformats",
        ]

        missing_keys = []
        for key in required_keys:
            if key not in self.parser[self.GC_SETTINGS]:
                missing_keys.append(key)

        if missing_keys:
            raise KeyError(
                f"Missing required config keys: {', '.join(missing_keys)}"
            )

    def get_url_list(self):
        """
        Returns all urls from url_list.ini
        """
        # Read in all lines from config file
        with open(self.url_config_path) as f:
            url_list = [line.rstrip() for line in f]

        # Remove first line "[URL LIST]"
        if len(url_list) > 0:
            url_list = url_list[1:]

        return url_list

    def get_boot_audio(self):
        """
        Returns full path to audio file named in general config
        """
        # Get file name from config
        audio_filename = self.parser[self.GC_SETTINGS]["boot_audio"]

        # Resolve path and return
        audio_path = self._get_audio_path(audio_filename)
        return audio_path

    def get_skip_intro(self):
        """
        Returns skip intro bool value
        """
        val = self.parser[self.GC_SETTINGS]["skip_intro"]
        return self._parse_bool(val)

    def get_output_dir(self):
        """
        Returns base directory for archive output (with ~ expanded)
        """
        output_dir = self.parser[self.GC_SETTINGS]["output_dir"]
        return str(Path(output_dir).expanduser())

    def get_archive_freq(self):
        """
        Returns the number of seconds to wait between archive runs
        """
        runtime = int(float(self.parser[self.GC_SETTINGS]["archive_frequency"]) * 3600)
        return runtime

    def get_oauth(self):
        """
        Returns Soundcloud OAuth value to enable HQ downloads
        """
        return self.parser[self.GC_SETTINGS]["oauth"]

    def get_hq_en(self):
        """
        Returns the True/False value for High Quality Enable
        """
        val = self.parser[self.GC_SETTINGS]["high_quality_enable"]
        return self._parse_bool(val)

    def get_sleep_interval_requests(self):
        """
        Returns sleep_interval_requests int value
        """
        val = self.parser[self.GC_SETTINGS]["rate_limit_sec"]
        return int(val)

    def get_listformats(self):
        """
        Returns listformats bool value
        """
        val = self.parser[self.GC_SETTINGS]["listformats"]
        return self._parse_bool(val)

    def get_initial_page_dl_limit(self) -> int:
        """
        Returns the initial page download limit.
        Returns -1 if no limit should be applied.
        """
        val = self.parser[self.GC_SETTINGS].get("initial_page_dl_limit", "-1")
        return int(val)

    def get_archived_page_dl_limit(self) -> int:
        """
        Returns the archived page download limit.
        Returns -1 if no limit should be applied.
        """
        val = self.parser[self.GC_SETTINGS].get("archived_page_dl_limit", "-1")
        return int(val)

    def get_state_db_path(self) -> str:
        """
        Returns the path to the archive state database file.
        """
        val = self.parser[self.GC_SETTINGS].get(
            "archive_db_path", "~/JDAE_OUTPUT/archive_db.json"
        )
        return str(Path(val).expanduser())
