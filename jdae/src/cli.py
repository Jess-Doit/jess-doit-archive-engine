"""
Command-line interface argument parsing for JDAE.
"""

import argparse
from typing import Dict, Any


def parse_arguments() -> Dict[str, Any]:
    """
    Parse command-line arguments for JDAE.

    Returns:
        Dictionary containing parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Jess' Archive Engine - Automated SoundCloud archiver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_jdae.py                    # Run with normal boot sequence
  python start_jdae.py --setup            # Interactive configuration wizard
  python start_jdae.py --skip-intro       # Skip boot sequence
  python start_jdae.py --dry-run          # Preview what would be downloaded
  python start_jdae.py --check-now        # Force immediate check instead of waiting
  python start_jdae.py --debug            # Enable debug logging
  python start_jdae.py --config myconfig.ini  # Use alternate config file
        """,
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run interactive configuration wizard",
    )

    parser.add_argument(
        "--skip-intro",
        action="store_true",
        help="Skip the boot sequence (no logo or audio)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview downloads without actually downloading",
    )

    parser.add_argument(
        "--check-now",
        action="store_true",
        help="Force immediate check of all URLs (don't wait for scheduled time)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug-level logging",
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to alternate gen_config.ini file",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Check URLs once and exit (don't loop continuously)",
    )

    args = parser.parse_args()

    return {
        "setup": args.setup,
        "skip_intro": args.skip_intro,
        "dry_run": args.dry_run,
        "check_now": args.check_now,
        "debug": args.debug,
        "config_path": args.config,
        "run_once": args.once,
    }
