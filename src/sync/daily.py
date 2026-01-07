"""Daily sync for data that updates daily."""

from datetime import date, timedelta

from src.client.derivatives import DerivativesClient
from src.client.equities import EquitiesClient
from src.client.financials import FinancialsClient
from src.client.indices import IndicesClient
from src.client.markets import MarketsClient
from src.config import Settings
from src.sync.base import BaseSync
from src.sync.transformers import TRANSFORMERS
from src.utils.date import today


class DailySync(BaseSync):
    """Daily synchronization for data that updates daily."""

    def __init__(self, settings: Settings | None = None, sync_date: date | None = None) -> None:
        """Initialize daily sync.

        Args:
            settings: Application settings
            sync_date: Date to sync (default: yesterday)
        """
        super().__init__(settings)
        self.sync_date = sync_date or (today() - timedelta(days=1))

    async def run(self) -> dict[str, int]:
        """Run daily sync for all daily tables.

        Returns:
            Dict mapping table names to records synced
        """
        results: dict[str, int] = {}
        self.logger.info("starting_daily_sync", sync_date=str(self.sync_date))

        # Daily tables
        results["eq_master"] = await self._sync_master()
        results["eq_bars_daily"] = await self._sync_bars_daily()
        results["fin_summary"] = await self._sync_fin_summary()
        results["eq_earnings_calendar"] = await self._sync_earnings_calendar()
        results["idx_bars_daily_topix"] = await self._sync_topix()
        results["idx_bars_daily"] = await self._sync_indices()
        results["mkt_short_ratio"] = await self._sync_short_ratio()
        results["mkt_short_sale"] = await self._sync_short_sale()
        results["mkt_margin_alert"] = await self._sync_margin_alert()
        results["drv_bars_daily_opt_225"] = await self._sync_options()

        self.logger.info("daily_sync_complete", results=results)
        return results

    async def _sync_master(self) -> int:
        """Sync master data for today."""
        table = "eq_master"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with EquitiesClient(self.settings) as client:
                data = await client.get_master(target_date=self.sync_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_bars_daily(self) -> int:
        """Sync daily bars for today."""
        table = "eq_bars_daily"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with EquitiesClient(self.settings) as client:
                data = await client.get_bars_daily_by_date(self.sync_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_fin_summary(self) -> int:
        """Sync financial summary for today."""
        table = "fin_summary"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with FinancialsClient(self.settings) as client:
                data = await client.get_summary_by_date(self.sync_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_earnings_calendar(self) -> int:
        """Sync earnings calendar."""
        table = "eq_earnings_calendar"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with FinancialsClient(self.settings) as client:
                data = await client.get_earnings_calendar()

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_topix(self) -> int:
        """Sync TOPIX data for today."""
        table = "idx_bars_daily_topix"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with IndicesClient(self.settings) as client:
                data = await client.get_topix(from_date=self.sync_date, to_date=self.sync_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_indices(self) -> int:
        """Sync indices data for today."""
        table = "idx_bars_daily"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with IndicesClient(self.settings) as client:
                data = await client.get_bars_daily_by_date(self.sync_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_short_ratio(self) -> int:
        """Sync short ratio data for today."""
        table = "mkt_short_ratio"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with MarketsClient(self.settings) as client:
                data = await client.get_short_ratio(target_date=self.sync_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_short_sale(self) -> int:
        """Sync short sale report for today."""
        table = "mkt_short_sale"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with MarketsClient(self.settings) as client:
                data = await client.get_short_sale_report(disc_date=self.sync_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_margin_alert(self) -> int:
        """Sync margin alert data for today."""
        table = "mkt_margin_alert"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with MarketsClient(self.settings) as client:
                data = await client.get_margin_alert(target_date=self.sync_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise

    async def _sync_options(self) -> int:
        """Sync Nikkei 225 options for today."""
        table = "drv_bars_daily_opt_225"
        started_at = self._log_sync_start(table, self.sync_date)

        try:
            async with DerivativesClient(self.settings) as client:
                data = await client.get_options_225(self.sync_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, self.sync_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, self.sync_date, started_at, e)
            raise
