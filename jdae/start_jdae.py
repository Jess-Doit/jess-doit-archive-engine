# Standard imports
import configparser
# import sys
import time
import traceback
import importlib.resources as import_resources

# Package imports
import jdae.src.logos as logos
from jdae.src.configmanager import ConfigManager

# 3rd Party imports
import pause
# import simpleaudio
# import pygame
# import pyaudio
# import wave
import yt_dlp
# from playsound import playsound


class JDAE(object):
    # Title to print before logo
    PRGM_TITLE = "Jess' Archive Engine"

    # Naming template for files output by downloader
    OUTPUT_FILE_TMPL = "%(title)s-%(id)s.%(ext)s"

    # Logger helper class
    # TODO: Move this outside to src
    class YTDLLogger(object):
        """
        Logger to print yt_dlp output
        """

        print_flag = False

        def debug(self, msg):
            """
            Print out relevant download information from yt_dlp
            """
            if self.print_flag:
                print(msg)
                self.print_flag = False
            elif msg.startswith("[download]"):
                print(msg)
                self.print_flag = True

        def warning(self, msg):
            """
            Print out warning messages from yt_dlp
            """
            print(f"Warning: {msg}")

        def error(self, msg):
            """
            Print out error messages from yt_dlp
            """
            print(f"Error: {msg}")

    def __init__(self):
        """
        Constructor for JDAE
        """
        self.cm = ConfigManager()

    def my_hook(self, d):
        """
        Hook for finished downloads
        """
        if d["status"] == "finished":
            print("Done downloading, now converting ...")

    def boot_sequence(self, audio):
        """
        Prints title + logo, and plays startup audio
        """
        print()
        print(self.PRGM_TITLE)
        # print(self.BOOT_LOGO)
        print(logos.BOOT_LOGO_80)
        # playsound(audio)

        # with wave.open(audio, "rb") as audio_wf:
        #     p = pyaudio.PyAudio()
        #     stream = p.open(
        #         format=p.get_format_from_width(audio_wf.getsamplewidth()),
        #         channels=audio_wf.getnchannels(),
        #         rate=audio_wf.getframerate(),
        #         output=True
        #     )

        #     while len(data := audio_wf.readframes(1024)):
        #         stream.write(data)

        #     stream.close()
        #     p.terminate()

        # pygame.init()
        # pygame.mixer.music.load(audio)
        # pygame.mixer.music.play()
        # pygame.event.wait()

        # wave = simpleaudio.WaveObject.from_wave_file(audio)
        # stream = wave.play()
        # stream.wait_done()

        print("\nStarting automated archive client")

    def download_from_url(self, ytdl, url):
        """
        Download all relevant media from url

        Skips media that has already been downloaded
        """
        try:
            ytdl.download([url])
        except:
            # TODO: Add debug mode and print stacktrace
            print(f"\nError occurred on page: {url}\n")

    def extract_info_url(self, ytdl, url):
        """
        List all media that will be downloaded from url
        """
        try:
            ytdl.extract_info(url, download=False)
        except:
            # TODO: debug mode and move these functions into diff file inside src
            print(f"\nError occurred on page: {url}\n")

    def main(self):
        """
        Main JDAE program logic. Starts up and runs archive automation.
        """
        # TODO: Add support for argparse (or should I just rely on config file?)

        # Read settings and urls from config files
        url_list = self.cm.get_url_list()
        audio = self.cm.get_boot_audio()
        output_dir = self.cm.get_output_dir()
        archive_wait_time = self.cm.get_archive_freq()
        oauth = self.cm.get_oauth()
        hq_en = self.cm.get_hq_en()

        # Print boot sequence and play audio
        if not self.cm.get_skip_intro():
            self.boot_sequence(audio)

        # Print list of pages to user that will be processed
        print("\nMonitoring the following pages:")
        for url in url_list:
            print(f" - {url}")

        # Construct output path template
        outtmpl = f"{output_dir}/archive/%(playlist)s/{self.OUTPUT_FILE_TMPL}"
        print("\n######")
        print(f"ARCHIVE OUTPUT DIRECTORY: {outtmpl}")
        print("######")

        if hq_en == "True":
            # Set header for HD Soundcould Downloads
            yt_dlp.utils.std_headers['Authorization'] = oauth

        # Options for yt_dlp instance
        ytdl_opts = {
            "format": "ba[acodec!*=opus]",
            "logger": self.YTDLLogger(),
            # 'progress_hooks': [self.my_hook],
            "outtmpl": outtmpl,
            # "listformats": True,
            "sleep_interval_requests": 3
        }
        # Time to get started
        print("\nEngine ready - good luck")
        time.sleep(4)
        try:
            # with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
            with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                while True:
                    # For every url in the url_list.ini run yt_dlp operation
                    for url in url_list:
                        # TODO: Make prints nicer or create gui experience and monitor output internally
                        print("\n######")
                        print(f"[URL] -- {url}\n")
                        # List all downloads available from url
                        # self.extract_info_url(ytdl, url)

                        # Download all media from url
                        self.download_from_url(ytdl, url)

                    print(
                        f"\nArchive pass completed. Will check again in {archive_wait_time}s ({archive_wait_time/3600}h)"
                    )
                    # This is better than time.sleep for large durations
                    # If archive_wait_time is 6 hours and the PC goes into sleep mode after 30 min
                    # time.sleep will still have 5h 30m on the sleep timer
                    # This method ensures that if 6 hours pass in real world time that the wait will be over
                    pause.seconds(archive_wait_time)
        except:
            traceback.print_exc()
            print(
                "\nArchive engine has failed. Please try again."
                "If the problem persists seek help ;)"
            )
            # TODO: Add debug run option and print stacktrace


if __name__ == "__main__":
    jdae = JDAE()
    jdae.main()
