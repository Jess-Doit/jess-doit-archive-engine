import time
#from __future__ import unicode_literals

import youtube_dl
from playsound import playsound


# URLs for testing
URL_0 = "https://www.youtube.com/watch?v=BaW_jenozKc"
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

# Logger to print various youtube_dl outputs
class MyLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def boot_sequence():
	print()
	print(PRGM_TITLE)
	print(BOOT_LOGO)
	playsound(AUDIO)
	print("\nStarting automated archive client")


def main():
	boot_sequence()
	
	# Options for youtube_dl instance
	ydl_opts = {
		'format': 'bestaudio/best',
		#'postprocessors': [{
		#    'key': 'FFmpegExtractAudio',
		#    'preferredcodec': 'mp3',
		#    'preferredquality': '192',
		#}],
		'logger': MyLogger(),
		'progress_hooks': [my_hook],
		'listformats' : True
	}

	#with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		#ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])
		#ydl.extract_info(URL_1, download=False)


if __name__ == "__main__":
	main()