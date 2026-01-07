#!/usr/bin/env python3
"""Run data synchronization."""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.sync.daily import DailySync
from src.sync.initial import InitialLoader
from src.sync.weekly import WeeklySync
from src.utils.date import parse_date
from src.utils.logging import get_logger, setup_logging


async def run_initial(args: argparse.Namespace) -> int:
    """Run initial bulk load."""
    logger = get_logger(__name__)
    settings = get_settings()

    if args.years:
        settings.initial_load_years = args.years

    resume = not args.no_resume
    logger.info("starting_initial_load", years=settings.initial_load_years, resume=resume)

    async with InitialLoader(settings, resume=resume) as loader:
        results = await loader.run()

    total = sum(results.values())
    logger.info("initial_load_complete", total_records=total, tables=results)
    print(f"Initial load complete: {total:,} records")
    return 0


async def run_daily(args: argparse.Namespace) -> int:
    """Run daily sync."""
    logger = get_logger(__name__)
    settings = get_settings()

    sync_date = parse_date(args.date) if args.date else None
    logger.info("starting_daily_sync", date=str(sync_date) if sync_date else "yesterday")

    async with DailySync(settings, sync_date) as sync:
        results = await sync.run()

    total = sum(results.values())
    logger.info("daily_sync_complete", total_records=total, tables=results)
    print(f"Daily sync complete: {total:,} records")
    return 0


async def run_weekly(args: argparse.Namespace) -> int:
    """Run weekly sync."""
    logger = get_logger(__name__)
    settings = get_settings()

    sync_date = parse_date(args.date) if args.date else None
    logger.info("starting_weekly_sync", date=str(sync_date) if sync_date else "last week")

    async with WeeklySync(settings, sync_date) as sync:
        results = await sync.run()

    total = sum(results.values())
    logger.info("weekly_sync_complete", total_records=total, tables=results)
    print(f"Weekly sync complete: {total:,} records")
    return 0


async def run_all(args: argparse.Namespace) -> int:
    """Run all syncs (daily + weekly)."""
    logger = get_logger(__name__)
    settings = get_settings()

    sync_date = parse_date(args.date) if args.date else None
    results: dict[str, int] = {}

    logger.info("starting_full_sync", date=str(sync_date) if sync_date else "auto")

    # Run daily sync
    async with DailySync(settings, sync_date) as sync:
        daily_results = await sync.run()
        results.update({f"daily_{k}": v for k, v in daily_results.items()})

    # Run weekly sync (only on appropriate days or if forced)
    today_weekday = datetime.now().weekday()
    if today_weekday in (1, 3) or args.force_weekly:  # Tuesday or Thursday
        async with WeeklySync(settings, sync_date) as sync:
            weekly_results = await sync.run()
            results.update({f"weekly_{k}": v for k, v in weekly_results.items()})

    total = sum(results.values())
    logger.info("full_sync_complete", total_records=total)
    print(f"Full sync complete: {total:,} records")
    return 0


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(
        description="Sync J-Quants data to DuckDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initial bulk load (10 years)
  python sync_all.py initial

  # Initial load with custom years
  python sync_all.py initial --years 5

  # Daily sync (yesterday's data)
  python sync_all.py daily

  # Daily sync for specific date
  python sync_all.py daily --date 2024-01-15

  # Weekly sync
  python sync_all.py weekly

  # Run all syncs
  python sync_all.py all
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Sync command")

    # Initial load
    initial_parser = subparsers.add_parser("initial", help="Initial bulk load")
    initial_parser.add_argument(
        "--years",
        type=int,
        help="Number of years to load (default: from settings)",
    )
    initial_parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start from scratch instead of resuming from last synced date",
    )

    # Daily sync
    daily_parser = subparsers.add_parser("daily", help="Daily sync")
    daily_parser.add_argument(
        "--date",
        type=str,
        help="Date to sync (YYYY-MM-DD, default: yesterday)",
    )

    # Weekly sync
    weekly_parser = subparsers.add_parser("weekly", help="Weekly sync")
    weekly_parser.add_argument(
        "--date",
        type=str,
        help="Date to sync (YYYY-MM-DD, default: last week)",
    )

    # All syncs
    all_parser = subparsers.add_parser("all", help="Run all syncs")
    all_parser.add_argument(
        "--date",
        type=str,
        help="Date to sync (YYYY-MM-DD)",
    )
    all_parser.add_argument(
        "--force-weekly",
        action="store_true",
        help="Force weekly sync regardless of day",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging()
    logger = get_logger(__name__)

    try:
        if args.command == "initial":
            return asyncio.run(run_initial(args))
        elif args.command == "daily":
            return asyncio.run(run_daily(args))
        elif args.command == "weekly":
            return asyncio.run(run_weekly(args))
        elif args.command == "all":
            return asyncio.run(run_all(args))
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        logger.warning("sync_interrupted")
        print("\nSync interrupted by user")
        return 130

    except Exception as e:
        logger.error("sync_failed", error=str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
