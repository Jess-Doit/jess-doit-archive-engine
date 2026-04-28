[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://black.readthedocs.io/en/stable/_static/license.svg)](https://github.com/Jess-Doit/jess-doit-archive-engine/blob/main/LICENSE)

# Jess Doit's Archive Engine (v1.0.0)
Automated tool to monitor your favorite SoundCloud pages. Ensure you never miss an upload with intelligent archiving, progress tracking, and smart retry logic.

**Completely automated SoundCloud backup with colored terminal UI, real-time progress tracking, and graceful error handling.**

<img src="https://github.com/Jess-Doit/jess-doit-resources/blob/main/jdae/boot.PNG?raw=true" alt="drawing" width="500"/>

## Features

- **Colored Terminal UI** - Beautiful colored output with cyan info, green success, red errors, yellow warnings
- **Progress Bars** - Real-time progress indicators with tqdm for visual feedback during archive passes
- **Interactive Setup Wizard** - `--setup` mode for first-time configuration with guided prompts
- **Summary Reports** - Detailed statistics after each pass (URLs checked, new downloads, skipped, errors, time elapsed)
- **Smart Retry Logic** - Automatic retry with exponential backoff (2s, 5s, 10s) for temporary failures
- **Real-time Status Tracking** - JSON status file shows current operation and progress
- **Graceful Shutdown** - Press Ctrl+C to cleanly exit with proper state cleanup
- **Download Limits** - Intelligent limiting (initial page vs archived page limits) to save bandwidth
- **Modular Architecture** - Clean separation of concerns with dependency injection
- **State Persistence** - Automatic tracking of downloaded files prevents re-downloads
- **Structured Logging** - Detailed logs with timestamps to `~/.JDAE_OUTPUT/archive.log`
- **Dry-run Mode** - Preview what would be downloaded without actually downloading
- **Multiple CLI Flags** - `--skip-intro`, `--dry-run`, `--check-now`, `--debug`, `--config`, `--once`
- **Cross-Platform** - Works on Windows, macOS, and Linux

## Getting Started

### Requirements
- Python 3.8 or newer (Python 3.12+ recommended)
- pip and setuptools

### Installation
1. Install Python 3 from https://www.python.org/downloads/
2. Clone or download this repository
3. Navigate to the directory and install:
   ```bash
   cd jess-doit-archive-engine
   pip install -U setuptools
   pip install -e .
   ```

### First Time Setup (Recommended)
Run the interactive setup wizard:
```bash
python -m jdae.start_jdae --setup
```

This will guide you through:
- Output directory selection (where downloads are saved)
- Archive check frequency (how often to scan for new uploads)
- Optional high-quality download settings (requires OAuth)
- Adding your first SoundCloud URL

### Manual Configuration
Alternatively, edit the config files directly:

1. **config/url_list.ini** - Add SoundCloud URLs (one per line):
   ```ini
   [urls]
   https://soundcloud.com/artist-name
   https://soundcloud.com/another-artist
   ```

2. **config/gen_config.ini** - Customize settings:
   ```ini
   [archive]
   OUTPUT_DIR=~/JDAE_OUTPUT
   ARCHIVE_FREQUENCY_SECONDS=21600  # 6 hours
   HQ_ENABLED=False
   INITIAL_PAGE_DL_LIMIT=999999
   ARCHIVED_PAGE_DL_LIMIT=5
   ```

## Running the Program

### Basic Usage
```bash
python -m jdae.start_jdae
```
Runs with boot sequence, displays logo and startup audio, then begins archiving.

### Common Commands

**Skip the boot sequence (faster startup):**
```bash
python -m jdae.start_jdae --skip-intro
```

**Preview what would be downloaded without downloading:**
```bash
python -m jdae.start_jdae --dry-run
```

**Check all URLs once then exit (instead of looping continuously):**
```bash
python -m jdae.start_jdae --once
```

**Force immediate check (don't wait for scheduled frequency):**
```bash
python -m jdae.start_jdae --check-now
```

**Enable debug logging for troubleshooting:**
```bash
python -m jdae.start_jdae --debug
```

**Use alternate config file:**
```bash
python -m jdae.start_jdae --config /path/to/custom_config.ini
```

**Combine flags:**
```bash
python -m jdae.start_jdae --skip-intro --dry-run --once
```

### Stopping the Program
Press **Ctrl+C** to gracefully shutdown. The program will:
- Save current state to prevent re-downloading
- Update status file with final statistics
- Print summary report
- Exit cleanly

## Accessing Your Downloads

Downloads are organized in the archive folder:
```
~/JDAE_OUTPUT/
├── archive/
│   ├── Artist Name (All)/      # Downloaded tracks
│   └── Another Artist/
├── archive.log                 # Detailed operation log
├── archive_db.json             # State database (prevents re-downloads)
└── status.json                 # Current operation status
```

Default location: `~/JDAE_OUTPUT` (~ = your home directory)
- Windows: `C:\Users\<USERNAME>\JDAE_OUTPUT`
- macOS: `/Users/<USERNAME>/JDAE_OUTPUT`
- Linux: `/home/<USERNAME>/JDAE_OUTPUT`

## Features Explained

### Colored Terminal Output
The program uses colors to make output easier to scan:
- **Cyan** - Informational messages
- **Green** - Successful operations
- **Red** - Errors
- **Yellow** - Warnings

### Progress Bars
Visual progress indicators show:
- Number of URLs processed
- Count of files downloaded in current pass
- Real-time updates as archiving progresses

### Summary Reports
After each archive pass, you see:
- Total URLs checked
- New files downloaded
- Files skipped (already archived)
- Errors encountered (with retry counts)
- Time elapsed for the pass
- When the next check will occur

Example:
```
════════════════════════════════════════════════════════════
                    PASS SUMMARY
════════════════════════════════════════════════════════════
URLs Checked: 3
New Downloads: 5
Skipped (Already Archived): 12
Errors (with Retry): 0
Permanently Skipped: 0

Time Elapsed: 2.5 minutes
Next Check In: 6.0 hours
```

### Smart Retry Logic
When a download fails temporarily:
1. Automatically retries (up to 3 times)
2. Waits between retries: 2 seconds, then 5 seconds, then 10 seconds
3. Distinguishes temporary errors (network) from permanent errors (URL not found)
4. Logs all retry attempts for debugging

### Real-Time Status File
While archiving, check `~/.JDAE_OUTPUT/status.json` to see:
```json
{
  "status": "downloading",
  "current_url": "https://soundcloud.com/artist",
  "progress": {
    "urls_checked": 1,
    "urls_total": 3,
    "attempted_downloads": 5,
    "successful_downloads": 3,
    "failed_downloads": 0,
    "skipped_downloads": 2
  },
  "last_updated": "2026-04-27T15:30:45.123456"
}
```

### State Persistence
The program maintains `archive_db.json` to track:
- What files have been downloaded (by unique ID)
- When each URL was last checked
- Error counts per URL
- Creation timestamps

This prevents re-downloading the same content across runs.

### Detailed Logging
All operations are logged to `archive.log`:
- Timestamps for every action
- Download successes and failures
- Retry attempts and backoff information
- Configuration details
- State updates

View logs:
```bash
tail -f ~/JDAE_OUTPUT/archive.log
```

## Troubleshooting

### "No URLs configured in url_list.ini"
**Solution:** Add at least one SoundCloud URL to `config/url_list.ini`

### "Invalid SoundCloud URL"
**Solution:** Ensure URLs are valid. Try in a browser first. Examples:
- Artist: `https://soundcloud.com/artist-name`
- Playlist: `https://soundcloud.com/artist-name/sets/playlist-name`
- Album: `https://soundcloud.com/artist-name/albums/album-name`
- Likes: `https://soundcloud.com/artist-name/likes`

### "Network timeout after 3 retries"
**Solution:** Check your internet connection. The program will retry automatically next cycle.

### Downloads going slowly
**Solution:** 
- Check `SLEEP_INTERVAL_REQUESTS` in `gen_config.ini` (currently 1 second between requests is respectful)
- Run with `--debug` flag to see what's happening
- Check your internet speed

### HQ downloads not working
**Solution:**
- Ensure `HQ_ENABLED=True` in config
- Provide valid SoundCloud OAuth token in `OAUTH` field
- See SoundCloud API documentation for getting OAuth tokens

### Program won't stop with Ctrl+C
**Solution:** Press Ctrl+C once. If stuck on download, may take a few seconds for yt-dlp to respond to interrupt signal.

## Architecture & Development

### Modular Design
The program is organized into independent, reusable modules:

```
jdae/
├── start_jdae.py       # Entry point
├── config/
│   ├── gen_config.ini  # Settings
│   └── url_list.ini    # URLs to monitor
└── src/
    ├── archiver.py         # Main orchestrator
    ├── downloader.py       # yt-dlp wrapper
    ├── logger.py           # Structured logging
    ├── state_manager.py    # Persistence layer
    ├── status_tracker.py   # Real-time tracking
    ├── ui.py               # Terminal UI
    ├── config_wizard.py    # Interactive setup
    ├── cli.py              # Argument parsing
    ├── configmanager.py    # Config loading
    └── logos.py            # ASCII art
```

Each module has a single responsibility and receives dependencies via constructor (dependency injection).

## Acknowledgments
- Built on top of the amazing [yt_dlp](https://github.com/yt-dlp/yt-dlp) library
- Terminal UI powered by [colorama](https://github.com/tartley/colorama) and [tqdm](https://github.com/tqdm/tqdm)
- Startup audio clips from [v1984](https://soundcloud.com/v1984)
- Original concept and development by Jess Doit

## License
MIT - See LICENSE file for details

## Support
For issues, bugs, or feature requests, please open an issue on the repository.
