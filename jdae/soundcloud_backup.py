import os
import subprocess
import sys
import time
import traceback


class YoutubeDL():
	"""
	Wrapper to control youtube-dl. Allows downloading of audio and video streams.
	"""
	YTDL_PATH = "/Program Files/youtube-dl/youtube-dl.exe"

	YTDL_CMD_LIST = "-F"
	YTDL_CMD_DL_BEST = "-f bestaudio"

	def __init__(self, url, path=None, output_dir=None):
		"""
		Parameters
		----------
		url : str
			URL of playlist to backup
		path : str
			Path to youtube-dl executable
		output_dir : str
			Path to output directory for downloads
		"""
		self.url = url

		# Set and validate ytdl execuatble path
		if path is None:
			self.path = self.YTDL_PATH
		else:
			self.path = path
		if not os.path.isfile(self.path):
			raise Exception(f"Youtube-dl executable not found at {path}")

		# Set and validate output directory
		pass
		# Create dir if it does not exist (raise exception)

	def get_url(self):
		"""
		Get value of self.url
		"""
		return self.url

	def get_path(self):
		"""
		Get value of self.path
		"""
		return self.path

	def list_all_tracks(self):
		"""
		Print a list of all tracks that ytdl can find from given playlist
		Uses self.url as playlist path
		"""
		self.list_all_tracks_url(self.url)

	def list_all_tracks_url(self, url):
		"""
		Print a list of all tracks that ytdl can find from given playlist
		Call with any URL

		Parameters
		----------
		url : str
			URL to playlist
		"""
		print("\n################")
		print(f"URL: {url}\n")
		result = subprocess.run(
			[self.path, self.YTDL_CMD_LIST, self.url],
			# stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL
		)
		return result.check_returncode()

	def _exec_tydl_cmd(self):
		"""
		"""
		pass


SC_URL_BASE = "https://soundcloud.com/"
SC_URL_LIKES = "likes/"
USERNAME = "jess-doit-223003857"


def main():
	"""
	Starts automated soundcloud backup service
	"""
	# Build path to playlist
	# likes_playlist_url = SC_URL_BASE + f"{USERNAME}/" + SC_URL_LIKES
	likes_playlist_url = "https://soundcloud.com/jess-doit-223003857/sets/natso-as"

	# Create ytdl instance
	try:
		ytdl = YoutubeDL(likes_playlist_url)
	except Exception:
		traceback.print_exc()
		sys.exit(1)

	# Print variables for debug
	print(f"YTDL: {ytdl.get_path()}")
	print(f"SC: {ytdl.get_url()}")

	ytdl.list_all_tracks()
	

if __name__ == "__main__":
	main()
