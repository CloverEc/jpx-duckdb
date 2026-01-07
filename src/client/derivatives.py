"""Derivatives API client for drv-bars-daily-opt-225 endpoint."""

from datetime import date
from typing import Any

from src.client.base import JQuantsClient
from src.utils.date import format_date


class DerivativesClient(JQuantsClient):
    """Client for derivatives endpoints."""

    async def get_options_225(self, target_date: date) -> list[dict[str, Any]]:
        """Get Nikkei 225 options OHLC and Greeks.

        Args:
            target_date: Target date (required)

        Returns:
            List of options bar records
        """
        params = {"date": format_date(target_date, with_hyphen=False)}
        return await self.fetch_all("/derivatives/bars/daily/options/225", params)
