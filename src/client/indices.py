"""Indices API client for idx-bars-daily and idx-bars-daily-topix endpoints."""

from datetime import date
from typing import Any

from src.client.base import JQuantsClient
from src.utils.date import format_date


class IndicesClient(JQuantsClient):
    """Client for index data endpoints."""

    async def get_topix(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get TOPIX OHLC data.

        Args:
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of TOPIX bar records
        """
        params: dict[str, Any] = {}
        if from_date:
            params["from"] = format_date(from_date, with_hyphen=False)
        if to_date:
            params["to"] = format_date(to_date, with_hyphen=False)

        return await self.fetch_all("/indices/bars/daily/topix", params)

    async def get_bars_daily(
        self,
        code: str | None = None,
        target_date: date | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get index OHLC data.

        Args:
            code: Index code (optional)
            target_date: Specific date (optional)
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of index bar records
        """
        params: dict[str, Any] = {}
        if code:
            params["code"] = code
        if target_date:
            params["date"] = format_date(target_date, with_hyphen=False)
        if from_date:
            params["from"] = format_date(from_date, with_hyphen=False)
        if to_date:
            params["to"] = format_date(to_date, with_hyphen=False)

        return await self.fetch_all("/indices/bars/daily", params)

    async def get_bars_daily_by_date(self, target_date: date) -> list[dict[str, Any]]:
        """Get all indices' daily bars for a specific date.

        Args:
            target_date: Target date

        Returns:
            List of index bar records
        """
        return await self.get_bars_daily(target_date=target_date)
