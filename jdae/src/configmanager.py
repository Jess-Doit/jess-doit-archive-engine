import configparser
import importlib.resources as import_resources


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

    def __init__(self):
        """
        ConfigManager constructor
        """
        # Get paths to ini config files
        self.gen_config_path = self._get_config_path(self.GEN_CONFIG)
        self.url_config_path = self._get_config_path(self.URL_CONFIG)

        # Create config parser and parse general config file
        self.parser = configparser.ConfigParser()
        self.parser.read(self.gen_config_path)

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

        # Convert string to bool value
        if val in ["True", "true"]:
            return True
        return False

    def get_output_dir(self):
        """
        Returns base directory for archive output
        """
        return self.parser[self.GC_SETTINGS]["output_dir"]

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

        # Convert string to bool value
        if val in ["True", "true"]:
            return True
        return False

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

        # Convert string to bool value
        if val in ["True", "true"]:
            return True
        return False
