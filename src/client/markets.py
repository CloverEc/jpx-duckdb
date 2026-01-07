"""Markets API client for market data endpoints."""

from datetime import date
from typing import Any

from src.client.base import JQuantsClient
from src.utils.date import format_date


class MarketsClient(JQuantsClient):
    """Client for market data endpoints."""

    async def get_calendar(
        self,
        hol_div: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get trading calendar.

        Args:
            hol_div: Holiday division code (optional)
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of calendar records
        """
        params: dict[str, Any] = {}
        if hol_div:
            params["hol_div"] = hol_div
        if from_date:
            params["from"] = format_date(from_date, with_hyphen=False)
        if to_date:
            params["to"] = format_date(to_date, with_hyphen=False)

        return await self.fetch_all("/markets/calendar", params)

    async def get_investor_types(
        self,
        section: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get trading by type of investors (weekly).

        Args:
            section: Market section (e.g., TSEPrime) (optional)
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of investor type records
        """
        params: dict[str, Any] = {}
        if section:
            params["section"] = section
        if from_date:
            params["from"] = format_date(from_date, with_hyphen=False)
        if to_date:
            params["to"] = format_date(to_date, with_hyphen=False)

        return await self.fetch_all("/equities/investor-types", params)

    async def get_margin_interest(
        self,
        code: str | None = None,
        target_date: date | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get weekly margin trading outstanding.

        Args:
            code: 5-digit stock code (optional)
            target_date: Specific date (optional)
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of margin interest records
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

        return await self.fetch_all("/markets/margin-interest", params)

    async def get_margin_interest_by_date(self, target_date: date) -> list[dict[str, Any]]:
        """Get margin interest data for a specific date.

        Args:
            target_date: Target date

        Returns:
            List of margin interest records
        """
        return await self.get_margin_interest(target_date=target_date)

    async def get_short_ratio(
        self,
        s33: str | None = None,
        target_date: date | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get short sale value and ratio by sector.

        Args:
            s33: 33-sector code (optional)
            target_date: Specific date (optional)
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of short ratio records
        """
        params: dict[str, Any] = {}
        if s33:
            params["s33"] = s33
        if target_date:
            params["date"] = format_date(target_date, with_hyphen=False)
        if from_date:
            params["from"] = format_date(from_date, with_hyphen=False)
        if to_date:
            params["to"] = format_date(to_date, with_hyphen=False)

        return await self.fetch_all("/markets/short-ratio", params)

    async def get_short_ratio_by_date(self, target_date: date) -> list[dict[str, Any]]:
        """Get short ratio data for a specific date.

        Args:
            target_date: Target date

        Returns:
            List of short ratio records
        """
        return await self.get_short_ratio(target_date=target_date)

    async def get_short_sale_report(
        self,
        code: str | None = None,
        disc_date: date | None = None,
        disc_date_from: date | None = None,
        disc_date_to: date | None = None,
        calc_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get outstanding short selling positions.

        Args:
            code: 5-digit stock code (optional)
            disc_date: Disclosure date (optional)
            disc_date_from: Disclosure date start (optional)
            disc_date_to: Disclosure date end (optional)
            calc_date: Calculation date (optional)

        Returns:
            List of short sale report records
        """
        params: dict[str, Any] = {}
        if code:
            params["code"] = code
        if disc_date:
            params["disc_date"] = format_date(disc_date, with_hyphen=False)
        if disc_date_from:
            params["disc_date_from"] = format_date(disc_date_from, with_hyphen=False)
        if disc_date_to:
            params["disc_date_to"] = format_date(disc_date_to, with_hyphen=False)
        if calc_date:
            params["calc_date"] = format_date(calc_date, with_hyphen=False)

        return await self.fetch_all("/markets/short-sale-report", params)

    async def get_short_sale_report_by_date(self, target_date: date) -> list[dict[str, Any]]:
        """Get short sale report data for a specific date.

        Args:
            target_date: Target disclosure date

        Returns:
            List of short sale report records
        """
        return await self.get_short_sale_report(disc_date=target_date)

    async def get_margin_alert(
        self,
        code: str | None = None,
        target_date: date | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get daily margin trading outstanding for stocks subject to daily publication.

        Args:
            code: 5-digit stock code (optional)
            target_date: Specific date (optional)
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of margin alert records
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

        return await self.fetch_all("/markets/margin-alert", params)

    async def get_margin_alert_by_date(self, target_date: date) -> list[dict[str, Any]]:
        """Get margin alert data for a specific date.

        Args:
            target_date: Target date

        Returns:
            List of margin alert records
        """
        return await self.get_margin_alert(target_date=target_date)
