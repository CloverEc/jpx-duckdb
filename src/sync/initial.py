"""Initial bulk load for historical data with concurrent fetching and resume support."""

import asyncio
from datetime import date
from typing import Any, Callable, Coroutine

from src.client.derivatives import DerivativesClient
from src.client.equities import EquitiesClient
from src.client.financials import FinancialsClient
from src.client.indices import IndicesClient
from src.client.markets import MarketsClient
from src.config import JQUANTS_DATA_START_DATE, Settings
from src.sync.base import BaseSync
from src.sync.transformers import TRANSFORMERS
from src.utils.date import get_trading_days, month_range, today, years_ago


class InitialLoader(BaseSync):
    """Initial bulk loader for historical data with concurrent fetching and resume support."""

    def __init__(self, settings: Settings | None = None, resume: bool = True) -> None:
        """Initialize loader.

        Args:
            settings: Application settings
            resume: If True, resume from last synced date (default: True)
        """
        super().__init__(settings)
        self.years = self.settings.initial_load_years
        self.resume = resume
        # Concurrent batch size (number of dates to fetch in parallel)
        self.concurrent_batch_size = self.settings.max_concurrent_requests

    def _get_resume_date(self, table: str) -> date | None:
        """Get the date to resume from for a table.

        Args:
            table: Table name

        Returns:
            Last synced date or None if no data exists
        """
        if not self.resume:
            return None

        try:
            # Get max date from table
            result = self.storage.conn.execute(
                f"SELECT MAX(date) FROM {table}"
            ).fetchone()
            if result and result[0]:
                self.logger.info(
                    "resuming_from",
                    table=table,
                    last_date=str(result[0]),
                )
                return result[0]
        except Exception:
            pass
        return None

    async def run(self) -> dict[str, int]:
        """Run initial load for all tables.

        Returns:
            Dict mapping table names to records loaded
        """
        results: dict[str, int] = {}

        # Calculate date range (respect API data start date limit)
        end_date = today()
        start_date = years_ago(self.years)
        # Ensure we don't go before API data start date
        if start_date < JQUANTS_DATA_START_DATE:
            start_date = JQUANTS_DATA_START_DATE
            self.logger.info(
                "adjusted_start_date",
                reason="API data not available before this date",
                adjusted_to=str(start_date),
            )
        self.logger.info(
            "starting_initial_load",
            start_date=str(start_date),
            end_date=str(end_date),
            years=self.years,
            concurrent_batch_size=self.concurrent_batch_size,
            resume=self.resume,
        )

        # Initialize schema
        self.storage.init_schema()

        # Load each table
        results["mkt_calendar"] = await self._load_calendar(start_date, end_date)
        results["eq_master"] = await self._load_master(start_date, end_date)
        results["eq_bars_daily"] = await self._load_bars_daily(start_date, end_date)
        results["fin_summary"] = await self._load_fin_summary(start_date, end_date)
        results["idx_bars_daily_topix"] = await self._load_topix(start_date, end_date)
        results["idx_bars_daily"] = await self._load_indices(start_date, end_date)
        results["eq_investor_types"] = await self._load_investor_types(start_date, end_date)
        results["mkt_margin_interest"] = await self._load_margin_interest(start_date, end_date)
        results["mkt_short_ratio"] = await self._load_short_ratio(start_date, end_date)
        results["mkt_short_sale"] = await self._load_short_sale(start_date, end_date)
        results["mkt_margin_alert"] = await self._load_margin_alert(start_date, end_date)
        results["drv_bars_daily_opt_225"] = await self._load_options(start_date, end_date)

        self.logger.info("initial_load_complete", results=results)
        return results

    async def _fetch_dates_concurrent(
        self,
        dates: list[date],
        fetch_func: Callable[[date], Coroutine[Any, Any, list[dict[str, Any]]]],
        table: str,
    ) -> tuple[int, int]:
        """Fetch data for multiple dates concurrently.

        Args:
            dates: List of dates to fetch
            fetch_func: Async function that fetches data for a single date
            table: Table name for transformation

        Returns:
            Tuple of (total_fetched, total_upserted)
        """
        total_fetched = 0
        total_upserted = 0
        transformer = TRANSFORMERS[table]

        # Process in batches
        for i in range(0, len(dates), self.concurrent_batch_size):
            batch_dates = dates[i : i + self.concurrent_batch_size]

            # Fetch concurrently
            tasks = [fetch_func(d) for d in batch_dates]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            all_records: list[dict[str, Any]] = []
            for j, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.warning(
                        "fetch_error",
                        table=table,
                        date=str(batch_dates[j]),
                        error=str(result),
                    )
                    continue

                if result:
                    total_fetched += len(result)
                    all_records.extend([transformer(r) for r in result])

            # Batch upsert
            if all_records:
                count = self.storage.upsert_batch(table, all_records)
                total_upserted += count

            # Log progress
            progress = min(i + self.concurrent_batch_size, len(dates))
            self.logger.info(
                "batch_progress",
                table=table,
                progress=f"{progress}/{len(dates)}",
                fetched=total_fetched,
            )

        return total_fetched, total_upserted

    async def _load_calendar(self, start_date: date, end_date: date) -> int:
        """Load trading calendar."""
        table = "mkt_calendar"
        started_at = self._log_sync_start(table, end_date)

        try:
            async with MarketsClient(self.settings) as client:
                data = await client.get_calendar(from_date=start_date, to_date=end_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, end_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_master(self, start_date: date, end_date: date) -> int:
        """Load master data concurrently by month."""
        table = "eq_master"
        started_at = self._log_sync_start(table, end_date)

        try:
            # Get month end dates
            month_ends = [month_end for _, month_end in month_range(start_date, end_date)]

            async with EquitiesClient(self.settings) as client:
                total_fetched, total_upserted = await self._fetch_dates_concurrent(
                    month_ends,
                    client.get_master_by_date,
                    table,
                )

            self._log_sync_complete(table, end_date, started_at, total_fetched, total_upserted)
            return total_upserted
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_bars_daily(self, start_date: date, end_date: date) -> int:
        """Load daily price data concurrently with resume support."""
        table = "eq_bars_daily"
        started_at = self._log_sync_start(table, end_date)

        try:
            # Check for resume point
            resume_date = self._get_resume_date(table)
            effective_start = resume_date if resume_date and resume_date > start_date else start_date

            # Get trading days (weekdays)
            trading_days = get_trading_days(effective_start, end_date)
            self.logger.info(
                "loading_bars_daily",
                start_date=str(effective_start),
                total_days=len(trading_days),
                concurrent_batch=self.concurrent_batch_size,
                resumed=resume_date is not None,
            )

            if not trading_days:
                self.logger.info("no_dates_to_sync", table=table)
                return 0

            async with EquitiesClient(self.settings) as client:
                total_fetched, total_upserted = await self._fetch_dates_concurrent(
                    trading_days,
                    client.get_bars_daily_by_date,
                    table,
                )

            self._log_sync_complete(table, end_date, started_at, total_fetched, total_upserted)
            return total_upserted
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_fin_summary(self, start_date: date, end_date: date) -> int:
        """Load financial summary data concurrently with resume support."""
        table = "fin_summary"
        started_at = self._log_sync_start(table, end_date)

        try:
            # Check for resume point (use disclosure_date)
            resume_date = None
            if self.resume:
                try:
                    result = self.storage.conn.execute(
                        "SELECT MAX(disclosure_date) FROM fin_summary"
                    ).fetchone()
                    if result and result[0]:
                        resume_date = result[0]
                        self.logger.info("resuming_from", table=table, last_date=str(resume_date))
                except Exception:
                    pass

            effective_start = resume_date if resume_date and resume_date > start_date else start_date
            trading_days = get_trading_days(effective_start, end_date)

            if not trading_days:
                self.logger.info("no_dates_to_sync", table=table)
                return 0

            async with FinancialsClient(self.settings) as client:
                total_fetched, total_upserted = await self._fetch_dates_concurrent(
                    trading_days,
                    client.get_summary_by_date,
                    table,
                )

            self._log_sync_complete(table, end_date, started_at, total_fetched, total_upserted)
            return total_upserted
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_topix(self, start_date: date, end_date: date) -> int:
        """Load TOPIX data."""
        table = "idx_bars_daily_topix"
        started_at = self._log_sync_start(table, end_date)

        try:
            async with IndicesClient(self.settings) as client:
                data = await client.get_topix(from_date=start_date, to_date=end_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, end_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_indices(self, start_date: date, end_date: date) -> int:
        """Load indices data concurrently by date."""
        table = "idx_bars_daily"
        started_at = self._log_sync_start(table, end_date)

        try:
            # Check for resume point
            resume_date = self._get_resume_date(table)
            effective_start = resume_date if resume_date and resume_date > start_date else start_date
            trading_days = get_trading_days(effective_start, end_date)

            if not trading_days:
                self.logger.info("no_dates_to_sync", table=table)
                return 0

            async with IndicesClient(self.settings) as client:
                total_fetched, total_upserted = await self._fetch_dates_concurrent(
                    trading_days,
                    client.get_bars_daily_by_date,
                    table,
                )

            self._log_sync_complete(table, end_date, started_at, total_fetched, total_upserted)
            return total_upserted
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_investor_types(self, start_date: date, end_date: date) -> int:
        """Load investor types data."""
        table = "eq_investor_types"
        started_at = self._log_sync_start(table, end_date)

        try:
            async with MarketsClient(self.settings) as client:
                data = await client.get_investor_types(from_date=start_date, to_date=end_date)

            records = [TRANSFORMERS[table](r) for r in data]
            count = self.storage.upsert_batch(table, records)
            self._log_sync_complete(table, end_date, started_at, len(data), count)
            return count
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_margin_interest(self, start_date: date, end_date: date) -> int:
        """Load margin interest data concurrently by date."""
        table = "mkt_margin_interest"
        started_at = self._log_sync_start(table, end_date)

        try:
            # Check for resume point
            resume_date = self._get_resume_date(table)
            effective_start = resume_date if resume_date and resume_date > start_date else start_date
            trading_days = get_trading_days(effective_start, end_date)

            if not trading_days:
                self.logger.info("no_dates_to_sync", table=table)
                return 0

            async with MarketsClient(self.settings) as client:
                total_fetched, total_upserted = await self._fetch_dates_concurrent(
                    trading_days,
                    client.get_margin_interest_by_date,
                    table,
                )

            self._log_sync_complete(table, end_date, started_at, total_fetched, total_upserted)
            return total_upserted
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_short_ratio(self, start_date: date, end_date: date) -> int:
        """Load short ratio data concurrently by date."""
        table = "mkt_short_ratio"
        started_at = self._log_sync_start(table, end_date)

        try:
            # Check for resume point
            resume_date = self._get_resume_date(table)
            effective_start = resume_date if resume_date and resume_date > start_date else start_date
            trading_days = get_trading_days(effective_start, end_date)

            if not trading_days:
                self.logger.info("no_dates_to_sync", table=table)
                return 0

            async with MarketsClient(self.settings) as client:
                total_fetched, total_upserted = await self._fetch_dates_concurrent(
                    trading_days,
                    client.get_short_ratio_by_date,
                    table,
                )

            self._log_sync_complete(table, end_date, started_at, total_fetched, total_upserted)
            return total_upserted
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_short_sale(self, start_date: date, end_date: date) -> int:
        """Load short sale report data concurrently by date."""
        table = "mkt_short_sale"
        started_at = self._log_sync_start(table, end_date)

        try:
            # Check for resume point
            resume_date = None
            if self.resume:
                try:
                    result = self.storage.conn.execute(
                        "SELECT MAX(disclosure_date) FROM mkt_short_sale"
                    ).fetchone()
                    if result and result[0]:
                        resume_date = result[0]
                        self.logger.info("resuming_from", table=table, last_date=str(resume_date))
                except Exception:
                    pass

            effective_start = resume_date if resume_date and resume_date > start_date else start_date
            trading_days = get_trading_days(effective_start, end_date)

            if not trading_days:
                self.logger.info("no_dates_to_sync", table=table)
                return 0

            async with MarketsClient(self.settings) as client:
                total_fetched, total_upserted = await self._fetch_dates_concurrent(
                    trading_days,
                    client.get_short_sale_report_by_date,
                    table,
                )

            self._log_sync_complete(table, end_date, started_at, total_fetched, total_upserted)
            return total_upserted
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_margin_alert(self, start_date: date, end_date: date) -> int:
        """Load margin alert data concurrently by date."""
        table = "mkt_margin_alert"
        started_at = self._log_sync_start(table, end_date)

        try:
            # Check for resume point
            resume_date = None
            if self.resume:
                try:
                    result = self.storage.conn.execute(
                        "SELECT MAX(pub_date) FROM mkt_margin_alert"
                    ).fetchone()
                    if result and result[0]:
                        resume_date = result[0]
                        self.logger.info("resuming_from", table=table, last_date=str(resume_date))
                except Exception:
                    pass

            effective_start = resume_date if resume_date and resume_date > start_date else start_date
            trading_days = get_trading_days(effective_start, end_date)

            if not trading_days:
                self.logger.info("no_dates_to_sync", table=table)
                return 0

            async with MarketsClient(self.settings) as client:
                total_fetched, total_upserted = await self._fetch_dates_concurrent(
                    trading_days,
                    client.get_margin_alert_by_date,
                    table,
                )

            self._log_sync_complete(table, end_date, started_at, total_fetched, total_upserted)
            return total_upserted
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise

    async def _load_options(self, start_date: date, end_date: date) -> int:
        """Load Nikkei 225 options data concurrently with resume support."""
        table = "drv_bars_daily_opt_225"
        started_at = self._log_sync_start(table, end_date)

        try:
            # Check for resume point
            resume_date = self._get_resume_date(table)
            effective_start = resume_date if resume_date and resume_date > start_date else start_date
            trading_days = get_trading_days(effective_start, end_date)

            if not trading_days:
                self.logger.info("no_dates_to_sync", table=table)
                return 0

            async with DerivativesClient(self.settings) as client:
                total_fetched, total_upserted = await self._fetch_dates_concurrent(
                    trading_days,
                    client.get_options_225,
                    table,
                )

            self._log_sync_complete(table, end_date, started_at, total_fetched, total_upserted)
            return total_upserted
        except Exception as e:
            self._log_sync_error(table, end_date, started_at, e)
            raise
