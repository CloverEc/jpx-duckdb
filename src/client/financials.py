"""Financials API client for fin-summary and eq-earnings-calendar endpoints."""

from datetime import date
from typing import Any

from src.client.base import JQuantsClient
from src.utils.date import format_date


class FinancialsClient(JQuantsClient):
    """Client for financial data endpoints."""

    async def get_summary(
        self,
        code: str | None = None,
        target_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get quarterly financial statements.

        Args:
            code: 5-digit stock code (required if no date)
            target_date: Disclosure date (required if no code)

        Returns:
            List of financial summary records
        """
        params: dict[str, Any] = {}
        if code:
            params["code"] = code
        if target_date:
            params["date"] = format_date(target_date, with_hyphen=False)

        return await self.fetch_all("/fins/summary", params)

    async def get_summary_by_date(self, target_date: date) -> list[dict[str, Any]]:
        """Get all financial disclosures for a specific date.

        Args:
            target_date: Disclosure date

        Returns:
            List of financial summary records
        """
        return await self.get_summary(target_date=target_date)

    async def get_summary_by_code(self, code: str) -> list[dict[str, Any]]:
        """Get all financial disclosures for a specific stock.

        Args:
            code: 5-digit stock code

        Returns:
            List of financial summary records
        """
        return await self.get_summary(code=code)

    async def get_earnings_calendar(self) -> list[dict[str, Any]]:
        """Get earnings announcement calendar.

        Returns next day's scheduled announcements.

        Returns:
            List of earnings calendar records
        """
        return await self.fetch_all("/equities/earnings-calendar")
