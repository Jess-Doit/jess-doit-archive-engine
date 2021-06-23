# Standard imports
import configparser
import time

# Package imports
from jdae.src.configmanager import ConfigManager

# 3rd Party imports
import youtube_dl
from playsound import playsound


class JDAE(object):
    # Boot audio clip (v1984)
    AUDIO = "./sounds/v1984_sound_studies-3.wav"

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
    """


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


    def my_hook(self, d):
        """
        Hook for finished downloads
        """
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')


    def boot_sequence(self):
        """
        Prints title + logo, and plays startup audio
        """
        print()
        print(self.PRGM_TITLE)
        print(self.BOOT_LOGO)
        playsound(self.AUDIO)
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

        # TODO: Add ability to skip boot sequence
        self.boot_sequence()

        # Options for youtube_dl instance
        ytdl_opts = {
            'format': 'bestaudio/best',
            'logger': self.YTDLLogger(),
            'progress_hooks': [self.my_hook],
            'listformats' : True
        }

        cm = ConfigManager()
        url_list = cm.get_url_list()

        print("\nMonitoring the following pages:")
        for url in url_list:
            print(f" - {url}")

        print("\nEngine ready - good luck")
        try:
            with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
                # For every url in the url_list.ini run youtube_dl operation
                for url in url_list:
                    # List all downloads available from url
                    self.extract_info_url(ytdl, url)

                    # Download all media from url
                    # self.download_from_url(ytdl, url)
        except:
            print(
                "Archive engine has failed. Please try again."
                "If the problem persists seek help ;)"
            )
            # TODO: Add debug run option and print stacktrace


if __name__ == "__main__":
    jdae = JDAE()
    jdae.main()
