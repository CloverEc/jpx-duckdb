#!/usr/bin/env python3
"""Initialize database schema."""

import argparse
import sys
from pathlib import Path

# Add src to path for running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.storage.duckdb import DuckDBStorage
from src.utils.logging import get_logger, setup_logging


def main() -> int:
    """Initialize database schema.

    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(description="Initialize J-Quants DuckDB database")
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to DuckDB file (default: from DUCKDB_PATH env)",
    )
    args = parser.parse_args()

    setup_logging()
    logger = get_logger(__name__)

    try:
        settings = get_settings()
        if args.db_path:
            settings.duckdb_path = Path(args.db_path)

        logger.info("initializing_database", path=str(settings.duckdb_path))

        with DuckDBStorage(settings) as storage:
            storage.init_schema()

        logger.info("database_initialized")
        print(f"Database initialized at: {settings.duckdb_path}")
        return 0

    except Exception as e:
        logger.error("initialization_failed", error=str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
