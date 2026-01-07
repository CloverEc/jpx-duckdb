"""Configuration management for jpx-duckdb."""

from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# J-Quants Standard Plan data starts from 2016-01-07
JQUANTS_DATA_START_DATE = date(2016, 1, 7)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # J-Quants API
    jquants_api_key: str = Field(..., description="J-Quants API key")
    jquants_base_url: str = Field(
        default="https://api.jquants.com/v2",
        description="J-Quants API base URL",
    )

    # DuckDB
    duckdb_path: Path = Field(
        default=Path("./data/jquants.duckdb"),
        description="Path to DuckDB database file",
    )

    # Rate limiting
    rate_limit_rps: float = Field(
        default=1.0,
        description="Requests per second",
    )
    max_concurrent_requests: int = Field(
        default=10,
        description="Maximum concurrent requests (batch size for parallel fetching)",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts",
    )
    backoff_factor: float = Field(
        default=2.0,
        description="Exponential backoff factor",
    )
    max_backoff: float = Field(
        default=60.0,
        description="Maximum backoff time in seconds",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )

    # Sync settings
    initial_load_years: int = Field(
        default=10,
        description="Number of years for initial load",
    )
    batch_size: int = Field(
        default=1000,
        description="Batch size for database inserts",
    )


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
