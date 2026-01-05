# jpx-duckdb

J-Quants API data storage with DuckDB - Japanese stock market data for analysis, backtesting, and ML.

## Features

- Fetch and store 5 years of Japanese stock market data
- 13 J-Quants API v2 endpoints (Standard Plan)
- DuckDB for fast analytical queries
- Daily/Weekly automatic synchronization
- Parquet export support

## Data Sources (J-Quants API v2 Standard Plan)

| # | Endpoint | Description |
|---|----------|-------------|
| 1 | eq-master | Listed issue information |
| 2 | eq-bars-daily | Stock prices (OHLCV) |
| 3 | fin-summary | Financial statements |
| 4 | eq-earnings-cal | Earnings calendar |
| 5 | mkt-cal | Trading calendar |
| 6 | eq-investor-types | Trading by investor type |
| 7 | idx-bars-daily-topix | TOPIX index |
| 8 | idx-bars-daily | Other indices |
| 9 | drv-bars-daily-opt-225 | Nikkei 225 options |
| 10 | mkt-margin-int | Weekly margin trading |
| 11 | mkt-short-ratio | Short sale ratio by sector |
| 12 | mkt-short-sale | Short selling positions |
| 13 | mkt-margin-alert | Daily margin trading |

## Quick Start

```bash
# Clone repository
git clone https://github.com/CloverEc/jpx-duckdb.git
cd jpx-duckdb

# Install dependencies
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env with your J-Quants API key

# Initialize database
python scripts/init_db.py

# Run initial sync (5 years)
python scripts/sync_all.py --initial --years 5

# Run daily sync
python scripts/sync_all.py --daily
```

## Documentation

- [LLM Development Guide](docs/LLM_DEVELOPMENT_GUIDE.md) - Complete API reference and development policy
- [DuckDB Schema](docs/duckdb_schema.md) - Database schema documentation

## License

MIT
