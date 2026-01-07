"""Base sync class with common functionality."""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any

from src.config import Settings, get_settings
from src.storage.duckdb import DuckDBStorage
from src.utils.logging import get_logger


class BaseSync(ABC):
    """Base class for data synchronization."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize sync.

        Args:
            settings: Application settings (default: from environment)
        """
        self.settings = settings or get_settings()
        self.logger = get_logger(self.__class__.__name__)
        self.storage = DuckDBStorage(settings)

    async def __aenter__(self) -> "BaseSync":
        """Async context manager entry."""
        self.storage.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        self.storage.close()

    @abstractmethod
    async def run(self) -> dict[str, int]:
        """Run synchronization.

        Returns:
            Dict mapping table names to records synced
        """
        ...

    def _log_sync_start(self, table: str, sync_date: date) -> datetime:
        """Log sync start and return start time."""
        started_at = datetime.now()
        self.logger.info("sync_started", table=table, sync_date=str(sync_date))
        return started_at

    def _log_sync_complete(
        self,
        table: str,
        sync_date: date,
        started_at: datetime,
        records_fetched: int,
        records_upserted: int,
    ) -> None:
        """Log sync completion and update metadata."""
        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()

        self.logger.info(
            "sync_completed",
            table=table,
            sync_date=str(sync_date),
            records_fetched=records_fetched,
            records_upserted=records_upserted,
            duration_seconds=duration,
        )

        self.storage.update_sync_metadata(table, sync_date, records_upserted, "success")
        self.storage.log_sync(
            table=table,
            sync_date=sync_date,
            started_at=started_at,
            completed_at=completed_at,
            records_fetched=records_fetched,
            records_inserted=records_upserted,
            records_updated=0,
            status="success",
        )

    def _log_sync_error(
        self,
        table: str,
        sync_date: date,
        started_at: datetime,
        error: Exception,
    ) -> None:
        """Log sync error."""
        self.logger.error(
            "sync_failed",
            table=table,
            sync_date=str(sync_date),
            error=str(error),
        )

        self.storage.update_sync_metadata(table, sync_date, 0, "failed")
        self.storage.log_sync(
            table=table,
            sync_date=sync_date,
            started_at=started_at,
            completed_at=datetime.now(),
            records_fetched=0,
            records_inserted=0,
            records_updated=0,
            status="failed",
            error_message=str(error),
        )
