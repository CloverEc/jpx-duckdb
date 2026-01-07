"""Weekly sync for data that updates weekly."""

from datetime import date, timedelta

from src.client.markets import MarketsClient
from src.config import Settings
from src.sync.base import BaseSync
from src.sync.transformers import TRANSFORMERS
from src.utils.date import today


class WeeklySync(BaseSync):
    """Weekly synchronization for data that updates weekly."""

    def __init__(self, settings: Settings | None = None, sync_date: date | None = None) -> None:
        """Initialize weekly sync.

        Args:
            settings: Application settings
            sync_date: Date to sync (default: last week)
        """
        super().__init__(settings)
        # Default to last week's data
        self.sync_date = sync_date or (today() - timedelta(days=7))

    async def run(self) -> dict[str, int]:
        """Run weekly sync for all weekly tables.

        Returns:
            Dict mapping table names to records synced
        """
        results: dict[str, int] = {}
        self.logger.info("starting_weekly_sync", sync_date=str(self.sync_date))

        # Weekly tables
        results["eq_investor_types"] = await self._sync_investor_types()
        results["mkt_margin_interest"] = await self._sync_margin_interest()

        self.logger.info("weekly_sync_complete", results=results)
        return results

    async def _sync_investor_types(self) -> int:
        """Sync investor types data for the week."""
        table = "eq_investor_types"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            # Get data for the week ending on sync_date
            week_start = self.sync_date - timedelta(days=6)

            async with MarketsClient(self.settings) as client:
                data = await client.get_investor_types(
                    from_date=week_start, to_date=self.sync_date
                )

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_margin_interest(self) -> int:
        """Sync margin interest data for the week."""
        table = "mkt_margin_interest"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            # Get data for the week ending on sync_date
            week_start = self.sync_date - timedelta(days=6)

            async with MarketsClient(self.settings) as client:
                data = await client.get_margin_interest(
                    from_date=week_start, to_date=self.sync_date
                )

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise
