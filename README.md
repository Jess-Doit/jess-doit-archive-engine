# Jess Doit's Archive Engine
Automated tool to monitor your favorite pages. Ensure you never miss an upload.
SoundCloud automatic backup.

## Getting started
- Install Python 3 (<=3.7)
- py -3 -m pip install -U setuptools
- clone repo
- cd jess-doit-archive-engine
- py -3 -m pip install -e .

## Setup config
- Check out program settings in config/gen_config.ini
- Edit list of urls. This is your backup list, everything here will have all media links downloaded
- Add one link per line. Can be any soundcloud page, playlist, album, likes page, etc...
- Save and you are ready to start

## Running the program
- Start a terminal/cmd prompt and cd to <repo_install_path>/jess-doit-archive-engine/jdae
- Run the starter program
- py -3 start_jdae.py
