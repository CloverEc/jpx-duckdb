"""Equities API client for eq-master and eq-bars-daily endpoints."""

from datetime import date
from typing import Any

from src.client.base import JQuantsClient
from src.utils.date import format_date


class EquitiesClient(JQuantsClient):
    """Client for equities endpoints."""

    async def get_master(
        self,
        code: str | None = None,
        target_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get listed issue information.

        Args:
            code: 5-digit stock code (optional)
            target_date: Target date (optional)

        Returns:
            List of master records
        """
        params: dict[str, Any] = {}
        if code:
            params["code"] = code
        if target_date:
            params["date"] = format_date(target_date, with_hyphen=False)

        return await self.fetch_all("/equities/master", params)

    async def get_master_by_date(self, target_date: date) -> list[dict[str, Any]]:
        """Get all stocks' master data for a specific date.

        Args:
            target_date: Target date

        Returns:
            List of master records for all stocks
        """
        return await self.get_master(target_date=target_date)

    async def get_bars_daily(
        self,
        code: str | None = None,
        target_date: date | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get daily OHLCV data.

        Args:
            code: 5-digit stock code (required if no date)
            target_date: Specific date (required if no code)
            from_date: Start date (optional, requires code)
            to_date: End date (optional, requires code)

        Returns:
            List of daily bar records
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

        return await self.fetch_all("/equities/bars/daily", params)

    async def get_bars_daily_by_date(self, target_date: date) -> list[dict[str, Any]]:
        """Get all stocks' daily bars for a specific date.

        Args:
            target_date: Target date

        Returns:
            List of daily bar records for all stocks
        """
        return await self.get_bars_daily(target_date=target_date)

    async def get_bars_daily_by_code(
        self,
        code: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get daily bars for a specific stock.

        Args:
            code: 5-digit stock code
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of daily bar records
        """
        return await self.get_bars_daily(code=code, from_date=from_date, to_date=to_date)
