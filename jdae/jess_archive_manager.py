# Standard imports
import configparser
import time

# Package imports
from jdae.src.configmanager import ConfigManager

# 3rd Party imports
import youtube_dl
from playsound import playsound


# URLs for testing
URL_0 = "https://soundcloud.com/cr_label/sets/cr003-plata-last-dayz"
URL_1 = "https://soundcloud.com/jess-doit-223003857/sets/natso-as"

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
        """
        if self.print_flag:
            print(msg)
            self.print_flag = False
        elif msg.startswith("[download]"):
            print(msg)
            self.print_flag = True

    def warning(self, msg):
        """
        """
        print(f"Warning: {msg}")

    def error(self, msg):
        """
        """
        print(f"Error: {msg}")


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def boot_sequence():
    """
    Prints title + logo, and plays startup audio
    """
    print()
    print(PRGM_TITLE)
    print(BOOT_LOGO)
    playsound(AUDIO)
    print("\nStarting automated archive client")


def download_from_url(url):
    """
    """
    pass


def extract_info_url(url):
    """
    """
    pass

def main():
    # TODO: Add support for argparse

    # TODO: Add ability to skip boot sequence
    boot_sequence()

    # Options for youtube_dl instance
    ydl_opts = {
        'format': 'bestaudio/best',
        'logger': YTDLLogger(),
        'progress_hooks': [my_hook],
        'listformats' : True
    }

    cm = ConfigManager()
    url_list = cm.get_url_list()

    print("\nMonitoring the following pages:")
    for url in url_list:
        print(f" - {url}")

    print("\nEngine ready - good luck")
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            #ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])
            for url in url_list:
                try:
                    ydl.extract_info(url, download=False)
                except DownloadError:
                    print("Error occurred on page: {url}")
                    print("Resuming...")
    except:
        print(
            "Archive engine has failed. Please try again."
            "If the problem persists seek help ;)"
        )
        # TODO: Add debug run option and print straktrace


if __name__ == "__main__":
    main()
