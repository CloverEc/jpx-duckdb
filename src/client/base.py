"""Base J-Quants API client with rate limiting and pagination."""

import asyncio
from typing import Any

import httpx

from src.config import Settings, get_settings
from src.utils.logging import get_logger


class APIError(Exception):
    """API request error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Authentication failed."""


class RateLimitError(APIError):
    """Rate limit exceeded."""


class JQuantsClient:
    """Base client for J-Quants API with rate limiting and pagination support."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize client.

        Args:
            settings: Application settings (default: from environment)
        """
        self.settings = settings or get_settings()
        self.logger = get_logger(__name__)

        # Rate limiting
        self._semaphore = asyncio.Semaphore(self.settings.max_concurrent_requests)
        self._last_request_time: float = 0
        self._min_interval = 1.0 / self.settings.rate_limit_rps

        # HTTP client
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "JQuantsClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.settings.jquants_base_url,
                headers={
                    "x-api-key": self.settings.jquants_api_key,
                    "Accept": "application/json",
                },
                timeout=httpx.Timeout(30.0),
                http2=True,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _wait_for_rate_limit(self) -> None:
        """Wait to respect rate limit."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make request with retry logic.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON

        Raises:
            APIError: On request failure after retries
            AuthenticationError: On 401 response
        """
        client = await self._ensure_client()
        last_error: Exception | None = None
        backoff = 1.0

        for attempt in range(self.settings.max_retries + 1):
            try:
                async with self._semaphore:
                    await self._wait_for_rate_limit()

                    self.logger.debug(
                        "api_request",
                        method=method,
                        path=path,
                        params=params,
                        attempt=attempt + 1,
                    )

                    response = await client.request(method, path, params=params)
                    response.raise_for_status()

                    return response.json()

            except httpx.HTTPStatusError as e:
                status = e.response.status_code

                if status == 401:
                    raise AuthenticationError("Invalid API key", status_code=401) from e

                if status == 429:
                    self.logger.warning(
                        "rate_limited",
                        path=path,
                        backoff=backoff,
                        attempt=attempt + 1,
                    )
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * self.settings.backoff_factor, self.settings.max_backoff)
                    last_error = RateLimitError(f"Rate limited: {e}", status_code=429)
                    continue

                # Other HTTP errors
                last_error = APIError(
                    f"HTTP {status}: {e.response.text[:200]}",
                    status_code=status,
                )
                if status >= 500:
                    # Retry server errors
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * self.settings.backoff_factor, self.settings.max_backoff)
                    continue
                raise last_error from e

            except httpx.RequestError as e:
                last_error = APIError(f"Request failed: {e}")
                self.logger.warning(
                    "request_error",
                    path=path,
                    error=str(e),
                    attempt=attempt + 1,
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * self.settings.backoff_factor, self.settings.max_backoff)

        raise last_error or APIError("Unknown error")

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make GET request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON
        """
        return await self._request_with_retry("GET", path, params)

    async def fetch_all(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        list_key: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch all pages of data.

        Args:
            path: API endpoint path
            params: Query parameters
            list_key: Key containing list data (auto-detected if None)

        Returns:
            Combined list from all pages
        """
        params = dict(params) if params else {}
        results: list[dict[str, Any]] = []
        page = 0

        while True:
            page += 1
            self.logger.debug("fetching_page", path=path, page=page)

            data = await self.get(path, params)

            # Auto-detect list key
            if list_key is None:
                for key in data:
                    if isinstance(data[key], list):
                        list_key = key
                        break

            if list_key and list_key in data:
                page_results = data[list_key]
                results.extend(page_results)
                self.logger.debug(
                    "page_fetched",
                    path=path,
                    page=page,
                    count=len(page_results),
                    total=len(results),
                )

            # Check for pagination
            pagination_key = data.get("pagination_key")
            if not pagination_key:
                break

            params["pagination_key"] = pagination_key

        self.logger.info(
            "fetch_complete",
            path=path,
            pages=page,
            total_records=len(results),
        )
        return results
