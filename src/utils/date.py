"""Date utility functions."""

from datetime import date, datetime, timedelta
from typing import Iterator


def parse_date(date_str: str) -> date:
    """Parse date string in various formats.

    Args:
        date_str: Date string (YYYY-MM-DD or YYYYMMDD)

    Returns:
        Parsed date object
    """
    date_str = date_str.strip()
    if "-" in date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return datetime.strptime(date_str, "%Y%m%d").date()


def format_date(d: date, with_hyphen: bool = True) -> str:
    """Format date to string.

    Args:
        d: Date object
        with_hyphen: If True, format as YYYY-MM-DD, else YYYYMMDD

    Returns:
        Formatted date string
    """
    if with_hyphen:
        return d.strftime("%Y-%m-%d")
    return d.strftime("%Y%m%d")


def today() -> date:
    """Get today's date."""
    return date.today()


def years_ago(years: int, from_date: date | None = None) -> date:
    """Get date N years ago.

    Args:
        years: Number of years
        from_date: Reference date (default: today)

    Returns:
        Date N years ago
    """
    ref = from_date or today()
    try:
        return ref.replace(year=ref.year - years)
    except ValueError:
        # Handle Feb 29 -> Feb 28
        return ref.replace(year=ref.year - years, day=28)


def date_range(
    start: date,
    end: date,
    step: timedelta | None = None,
) -> Iterator[date]:
    """Generate dates in range.

    Args:
        start: Start date (inclusive)
        end: End date (inclusive)
        step: Step size (default: 1 day)

    Yields:
        Dates in range
    """
    if step is None:
        step = timedelta(days=1)

    current = start
    while current <= end:
        yield current
        current += step


def month_range(start: date, end: date) -> Iterator[tuple[date, date]]:
    """Generate month ranges between start and end dates.

    Args:
        start: Start date
        end: End date

    Yields:
        Tuples of (month_start, month_end)
    """
    current = start.replace(day=1)
    while current <= end:
        month_start = max(current, start)
        # Get last day of month
        if current.month == 12:
            next_month = current.replace(year=current.year + 1, month=1)
        else:
            next_month = current.replace(month=current.month + 1)
        month_end = min(next_month - timedelta(days=1), end)

        yield month_start, month_end

        current = next_month


def get_trading_days(start: date, end: date) -> list[date]:
    """Get list of weekdays (potential trading days).

    Note: This does not account for holidays. Use mkt_calendar for accurate trading days.

    Args:
        start: Start date
        end: End date

    Returns:
        List of weekdays
    """
    return [d for d in date_range(start, end) if d.weekday() < 5]


def is_weekday(d: date) -> bool:
    """Check if date is a weekday."""
    return d.weekday() < 5
