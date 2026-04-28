"""
Entry point for JDAE (Jess' Archive Engine).
Minimal startup script that initializes all components and starts archiving.
"""

from jdae.src.cli import parse_arguments
from jdae.src.configmanager import ConfigManager
from jdae.src.logger import ArchiveLogger
from jdae.src.state_manager import StateManager
from jdae.src.downloader import ArchiveDownloader
from jdae.src.archiver import Archiver


def main():
    """
    Main entry point for JDAE.
    Initializes all components and starts the archive engine.
    """
    # Parse command-line arguments
    args = parse_arguments()

    try:
        # Initialize ConfigManager (with optional custom config path)
        config = ConfigManager(custom_config_path=args.get("config_path"))

        # Get configuration values
        output_dir = config.get_output_dir()
        oauth = config.get_oauth()
        hq_enabled = config.get_hq_en()
        rate_limit = config.get_sleep_interval_requests()
        listformats = config.get_listformats()

        # Initialize Logger
        debug_mode = args.get("debug", False)
        logger = ArchiveLogger(output_dir, debug=debug_mode)
        logger.info("JDAE starting up")
        logger.debug(f"Debug mode: {debug_mode}")

        # Initialize StateManager
        state_db_path = config.get_state_db_path()
        state_manager = StateManager(state_db_path, logger)

        # Initialize Downloader
        downloader = ArchiveDownloader(
            output_dir=output_dir,
            logger=logger,
            oauth=oauth,
            hq_enabled=hq_enabled,
            rate_limit_sec=rate_limit,
            listformats=listformats,
        )

        # Initialize Archiver
        archiver = Archiver(
            config_manager=config,
            logger=logger,
            state_manager=state_manager,
            downloader=downloader,
            skip_intro=args.get("skip_intro", False),
            dry_run=args.get("dry_run", False),
        )

        # Determine whether to run once or continuously
        run_once = args.get("run_once", False)
        if args.get("check_now"):
            # --check-now implies run once
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
