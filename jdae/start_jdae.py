# Standard imports
import configparser
import time
import importlib.resources as import_resources

# Package imports
from jdae.src.configmanager import ConfigManager

# 3rd Party imports
import youtube_dl
from playsound import playsound


class JDAE(object):
    # Title and logo
    PRGM_TITLE = "Jess' Archive Engine"
    BOOT_LOGO = """
    yyyyyyyyyyyyyssssyhhhhhhysso+y+/:--````..-:+osyhhhhhhhhhhdmNMMMMMMMMMMMMMMMMMMMM
    yyyyyyhhdddhssssoso+///y+/+/yos:hys/.`.````````-:+ymNMMMMMMMMMMMMMMMMMMMMMMMMMMM
    yyyhdmdhyyyssysooooooooss+++smmdmdhhd::..........``.:odmNNMMMMMMMMMMMMMMMMMMMMMM
    hdddhyyyyysyyyyhhhyysssooo++/ydmmmdyd/:-.............``-+yhhhhddmNMMMMMMMMMMMMMM
    hyyyyyyyyyhhhhyyssssssssso++/--:/++o/:-.................`./yhhhhysyhdNMMMMMMMMMM
    yyyyyyyysyyssssssssssyyys++++//::---..----::/-............`.omNNNmdyssydNMMMMMMM
    yyyyyyysyyysssssssyyydso++++++++++++++/////////.............`-hNNMMMNhsoshNMMMMM
    yyyyyysyyyyssyyhhdddhsoooooo++++++++++++++//////:-...........``/hmmNMMNhsoshNMMM
    yyyyyssyyyhdmmNmddhooooooooooooo++++++++++++++////////++-......`-ymmmNMMmyoosdMM
    yyyyysyhdmNNNmdhhysssoooooooooooooooo++++++++++++++//+++/::--...`.+dNNNNMNhsooyN
    yyyyydmmNNNmdhhysssssssssoooooooooooooooo++++++++++++o++///////::-.-smNNNNMdsoos
    yhddmNNNNmdyhhysssssyysoooossoooooooooooooooo++++++++o+++++/////////:/NNNNNNmso:
    dmmdNmmmhyyhhyyyyyhy+//////++o++ooooooooooooooooo++++++++++++++/////:-NNNNNNNy-.
    NNdmdhhyyyhhyyyyydy/:/++/////+/..+ssssooooooooooooooo++++++++++++++:`sNNNNNNh-..
    ddhhhyyyyhhyyyyyddyh/sdddds//sso//ssssssssooooooooooooooo+++++++++-`/mNNNNNm:--:
    Ndmmmmmmmmdddddhmmmmdhmddmmdoyssssssssssssssssooooooooooooooo++++.`-+oymNNms////
    NdNNNmmddddhhhhhhNmmmNNNmhmmhyyyyyyyyyyyssssssssssooooooooooo++/-.-/::-:+/:---..
    NdNNNNNmmmmmdddddmmmmmmdmdmdyyyyyyyyyyyyyhhhhhysssssssso+/:-----................
    NdNNNNNNNNNNNNNNNNmmmmdddhhyyyyhhhddmmmmNNNNNdsssssso+:-..........---:::::::::::
    NdNNNNNNNNNNNNmmdhhhdhhhhdddmmmNNNmNNNNNNNNNdysssso/-.......-::/++++++oooooooooo
    mdNNNNNNNNmmdddhhhhhddmNNNNNNNNNNNNNNNNNNNmmyyyys/-......-/+oooooooooooooooooooo
    NdNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNmdhyyhdms-......:+ossssssssssssssssssssss

    soundcloud.com/jess-doit-223003857
    """

    OUTPUT_FILE_TMPL = "%(title)s-%(id)s.%(ext)s"

    # Logger helper class
    class YTDLLogger(object):
        """
        Logger to print youtube_dl output
        """

        print_flag = False

        def debug(self, msg):
            """
            Print out relevant download information from youtube_dl
            """
            if self.print_flag:
                print(msg)
                self.print_flag = False
            elif msg.startswith("[download]"):
                print(msg)
                self.print_flag = True

        def warning(self, msg):
            """
            Print out warning messages from youtube_dl
            """
            print(f"Warning: {msg}")

        def error(self, msg):
            """
            Print out error messages from youtube_dl
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
        print(self.BOOT_LOGO)
        playsound(audio)
        print("\nStarting automated archive client")

    def download_from_url(self, ytdl, url):
        """
        Download all relevant media from url

        Skips media that has already been downloaded
        """
        try:
            ytdl.download([url])
        except DownloadError:
            print(f"\nError occurred on page: {url}\n")

    def extract_info_url(self, ytdl, url):
        """
        List all media that will be downloaded from url
        """
        try:
            ytdl.extract_info(url, download=False)
        except DownloadError:
            print(f"\nError occurred on page: {url}\n")

    def main(self):
        """
        Main JDAE program logic. Starts up and runs archive automation.
        """
        # TODO: Add support for argparse

        # Read settings and urls from config files
        url_list = self.cm.get_url_list()
        audio = self.cm.get_boot_audio()
        output_dir = self.cm.get_output_dir()
        archive_wait_time = self.cm.get_archive_freq()

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

        # Options for youtube_dl instance
        ytdl_opts = {
            "format": "bestaudio/best",
            "logger": self.YTDLLogger(),
            #'progress_hooks': [self.my_hook],
            "outtmpl": outtmpl,
            # "listformats": True,
        }
        # Time to get started
        print("\nEngine ready - good luck")
        time.sleep(4)
        try:
            with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
                while True:
                    # For every url in the url_list.ini run youtube_dl operation
                    for url in url_list:
                        print(f"\n[URL] -- {url}\n")
                        # List all downloads available from url
                        # self.extract_info_url(ytdl, url)

                        # Download all media from url
                        self.download_from_url(ytdl, url)

                    print(
                        f"\nArchive pass completed. Will check again in {archive_wait_time}s ({archive_wait_time/3600}h)"
                    )
                    time.sleep(archive_wait_time)
        except:
            print(
                "Archive engine has failed. Please try again."
                "If the problem persists seek help ;)"
            )
            # TODO: Add debug run option and print stacktrace


if __name__ == "__main__":
    jdae = JDAE()
    jdae.main()
