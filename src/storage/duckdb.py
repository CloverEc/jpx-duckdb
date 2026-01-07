"""DuckDB storage operations."""

from datetime import date, datetime
from pathlib import Path
from typing import Any

import duckdb

from src.config import Settings, get_settings
from src.storage.schema import create_all_tables
from src.utils.logging import get_logger


class DuckDBStorage:
    """DuckDB storage manager."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize storage.

        Args:
            settings: Application settings (default: from environment)
        """
        self.settings = settings or get_settings()
        self.logger = get_logger(__name__)
        self._conn: duckdb.DuckDBPyConnection | None = None

    def __enter__(self) -> "DuckDBStorage":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        if self._conn is None:
            # Ensure directory exists
            db_path = self.settings.duckdb_path
            db_path.parent.mkdir(parents=True, exist_ok=True)

            self._conn = duckdb.connect(str(db_path))
            self.logger.info("database_connected", path=str(db_path))

        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            self.logger.info("database_closed")

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get active connection."""
        if self._conn is None:
            return self.connect()
        return self._conn

    def init_schema(self) -> None:
        """Initialize database schema."""
        self.logger.info("initializing_schema")
        create_all_tables(self.conn)
        self.logger.info("schema_initialized")

    def upsert(
        self,
        table: str,
        records: list[dict[str, Any]],
        columns: list[str] | None = None,
    ) -> int:
        """Insert or replace records.

        Args:
            table: Table name
            records: List of record dictionaries
            columns: Column names (auto-detected if None)

        Returns:
            Number of records upserted
        """
        if not records:
            return 0

        # Auto-detect columns from first record
        if columns is None:
            columns = list(records[0].keys())

        # Create temp table and insert
        temp_table = f"_temp_{table}"
        col_list = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])

        # Prepare values
        values = [[record.get(col) for col in columns] for record in records]

        try:
            # Create temp table with same structure
            self.conn.execute(f"CREATE TEMP TABLE IF NOT EXISTS {temp_table} AS SELECT * FROM {table} WHERE 1=0")
            self.conn.execute(f"DELETE FROM {temp_table}")

            # Insert into temp table
            self.conn.executemany(
                f"INSERT INTO {temp_table} ({col_list}) VALUES ({placeholders})",
                values,
            )

            # Upsert from temp to main table
            self.conn.execute(f"INSERT OR REPLACE INTO {table} SELECT * FROM {temp_table}")

            self.logger.debug("upsert_complete", table=table, count=len(records))
            return len(records)

        finally:
            self.conn.execute(f"DROP TABLE IF EXISTS {temp_table}")

    def upsert_batch(
        self,
        table: str,
        records: list[dict[str, Any]],
        columns: list[str] | None = None,
        batch_size: int | None = None,
    ) -> int:
        """Insert or replace records in batches.

        Args:
            table: Table name
            records: List of record dictionaries
            columns: Column names (auto-detected if None)
            batch_size: Batch size (default from settings)

        Returns:
            Total number of records upserted
        """
        if not records:
            return 0

        batch_size = batch_size or self.settings.batch_size
        total = 0

        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            total += self.upsert(table, batch, columns)

        self.logger.info("batch_upsert_complete", table=table, total=total)
        return total

    def get_last_sync_date(self, table: str) -> date | None:
        """Get last sync date for a table.

        Args:
            table: Table name

        Returns:
            Last sync date or None
        """
        result = self.conn.execute(
            "SELECT last_sync_date FROM sync_metadata WHERE table_name = ?",
            [table],
        ).fetchone()
        return result[0] if result else None

    def update_sync_metadata(
        self,
        table: str,
        sync_date: date,
        records_synced: int,
        status: str = "success",
    ) -> None:
        """Update sync metadata.

        Args:
            table: Table name
            sync_date: Sync date
            records_synced: Number of records synced
            status: Sync status
        """
        self.conn.execute(
            """
            INSERT OR REPLACE INTO sync_metadata
            (table_name, last_sync_date, last_sync_timestamp, records_synced, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            [table, sync_date, datetime.now(), records_synced, status],
        )

    def log_sync(
        self,
        table: str,
        sync_date: date,
        started_at: datetime,
        completed_at: datetime | None,
        records_fetched: int,
        records_inserted: int,
        records_updated: int,
        status: str,
        error_message: str | None = None,
    ) -> None:
        """Log sync operation.

        Args:
            table: Table name
            sync_date: Sync date
            started_at: Start timestamp
            completed_at: Completion timestamp
            records_fetched: Records fetched from API
            records_inserted: Records inserted
            records_updated: Records updated
            status: Sync status
            error_message: Error message if failed
        """
        self.conn.execute(
            """
            INSERT INTO sync_log
            (table_name, sync_date, started_at, completed_at,
             records_fetched, records_inserted, records_updated, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                table,
                sync_date,
                started_at,
                completed_at,
                records_fetched,
                records_inserted,
                records_updated,
                status,
                error_message,
            ],
        )

    def query(self, sql: str, params: list[Any] | None = None) -> list[tuple[Any, ...]]:
        """Execute query and return results.

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            List of result tuples
        """
        if params:
            return self.conn.execute(sql, params).fetchall()
        return self.conn.execute(sql).fetchall()

    def query_df(self, sql: str, params: list[Any] | None = None) -> "pandas.DataFrame":  # noqa: F821
        """Execute query and return DataFrame.

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            Pandas DataFrame
        """
        if params:
            return self.conn.execute(sql, params).fetchdf()
        return self.conn.execute(sql).fetchdf()
