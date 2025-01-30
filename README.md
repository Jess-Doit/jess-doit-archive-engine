[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://black.readthedocs.io/en/stable/_static/license.svg)](https://github.com/Jess-Doit/jess-doit-archive-engine/blob/main/LICENSE)

# Jess Doit's Archive Engine
Automated tool to monitor your favorite pages. Ensure you never miss an upload.
SoundCloud automatic backup

Add your favorite pages to the list in url_lists.ini and this program will automatically backup all songs from that page.
This process is completely automated and by default will check each page every 6 hours. This and other settings can be controlled by modifying `gen_config.ini`.

<img src="https://github.com/Jess-Doit/jess-doit-resources/blob/main/jdae/boot.PNG?raw=true" alt="drawing" width="500"/>

## Getting started
- Install Python 3 (3.8 or newer, recommended latest)
  - Go to https://www.python.org/downloads/ and install the latest version of Python 3 for your OS
- Use pip to install setuptools
  - `pip install -U setuptools`
- Clone repo or download the repo zip and unpack somewhere on your computer
- Navigate to the directory in your terminal and then pip install this repo
  - `cd jess-doit-archive-engine`
  - `pip install -e .`

## Setup config
- All user configurable files live in the config folder
- Config files have .ini extension but you can view/edit them like .txt files
- Check out program settings in `config/gen_config.ini`
- Modify whatever you would like. Restore to defaults if somethings goes wrong
- You can run the program without and changes here. The default settings should work fine
- Important to note the file `config/url_list.ini`
- In this file place 1 url per line
- Change to whatever SoundCloud links you want the archive engine to monitor
- Edit this list of urls. This is your backup list, everything here will have all media links downloaded
- Add one link per line. Can be any soundcloud page, playlist, album, likes page, etc...
- Save and you are ready to start

## Running the program
- Start a terminal/cmd prompt and `cd <repo_install_path>/jess-doit-archive-engine/jdae`
- Run the starter program
  - `python start_jdae.py`
- The program will print some info to the console and then start interating over the links on the pages set in url_list.ini
- Kill the program with Ctrl+C in the window. You might need to do it twice

## Accessing your downloads
- Check the config file for the output_dir value
- By default the archive saves to `~/JDAE_OUTPUT`
- "~" means home directory. On Windows this is `C:\users\<USERNAME>`, on Mac this is `/Users/<USERNAME>`
- So look for a folder called `JDAE_OUTPUT` inside of your user directory

## Acknowledgments
- Built on top of the amazing yt_dlp python library https://github.com/yt-dlp/yt-dlp
- Startup audio clips from https://soundcloud.com/v1984/2014-sound-logo-studies
- Support the artist https://soundcloud.com/v1984
