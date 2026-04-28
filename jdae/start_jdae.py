"""
Entry point for JDAE (Jess' Archive Engine).
Minimal startup script that initializes all components and starts archiving.
"""

from jdae.src.cli import parse_arguments
from jdae.src.config_wizard import run_setup_wizard
from jdae.src.configmanager import ConfigManager
from jdae.src.logger import ArchiveLogger
from jdae.src.state_manager import StateManager
from jdae.src.status_tracker import StatusTracker
from jdae.src.downloader import ArchiveDownloader
from jdae.src.archiver import Archiver
from jdae.src.ui import get_ui


def main():
    """
    Main entry point for JDAE.
    Initializes all components and starts the archive engine.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Handle setup wizard
    if args.get("setup"):
        ui = get_ui()
        if run_setup_wizard():
            ui.print_success("Setup complete! Run 'python start_jdae.py' to start archiving")
        return

    try:
        # Initialize UI
        ui = get_ui(verbose=args.get("debug", False))

        # Initialize ConfigManager (with optional custom config path)
        config = ConfigManager(custom_config_path=args.get("config_path"))

        # Merge config and CLI options (CLI takes precedence)
        # For debug_mode: CLI --debug flag overrides config value
        debug_mode = args.get("debug") if args.get("debug") is not None else config.get_debug_mode()
        
        # For run_once: CLI --once flag overrides config value
        run_once = args.get("run_once") if args.get("run_once") is not None else config.get_run_once_mode()

        # Get configuration values
        output_dir = config.get_output_dir()
        oauth = config.get_oauth()
        hq_enabled = config.get_hq_en()
        rate_limit = config.get_sleep_interval_requests()
        listformats = config.get_listformats()

        # Initialize Logger
        logger = ArchiveLogger(output_dir, debug=debug_mode)
        logger.info("JDAE starting up")
        logger.debug(f"Debug mode: {debug_mode}")

        # Initialize StateManager
        state_db_path = config.get_state_db_path()
        state_manager = StateManager(state_db_path, logger)

        # Initialize StatusTracker
        status_file = f"{output_dir}/status.json"
        status_tracker = StatusTracker(status_file, logger)

        # Initialize Downloader
        downloader = ArchiveDownloader(
            output_dir=output_dir,
            logger=logger,
            oauth=oauth,
            hq_enabled=hq_enabled,
            rate_limit_sec=rate_limit,
            listformats=listformats,
        )

        # Initialize Archiver (pass UI for display)
        archiver = Archiver(
            config_manager=config,
            logger=logger,
            state_manager=state_manager,
            status_tracker=status_tracker,
            downloader=downloader,
            skip_intro=args.get("skip_intro", False),
            dry_run=args.get("dry_run", False),
        )

        # Check for --check-now flag which implies single-run
        if args.get("check_now"):
            run_once = True

        # Start the archive engine
        archiver.run(run_once=run_once)

    except KeyboardInterrupt:
        print("\nArchive engine stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
