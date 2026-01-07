# Database User Guide

A guide for analysts and feature creators working with the J-Quants DuckDB database.

---

## Quick Start

```python
import duckdb

# Connect to database
conn = duckdb.connect('data/jquants.duckdb', read_only=True)

# Query example
df = conn.execute("""
    SELECT code, company_name, adj_close
    FROM eq_bars_daily b
    JOIN eq_master m USING (date, code)
    WHERE b.date = '2024-01-15'
    ORDER BY turnover DESC
    LIMIT 10
""").fetchdf()
```

---

## Database Schema Overview

### Core Tables

| Table | Description | Update Freq | Primary Key |
|-------|-------------|-------------|-------------|
| `eq_master` | Stock master data (name, sector, market) | Daily | (date, code) |
| `eq_bars_daily` | Daily OHLCV + adjusted prices | Daily | (date, code) |
| `fin_summary` | Quarterly financials | Daily | (code, disclosure_date, disclosure_no) |
| `idx_bars_daily` | Index OHLCV (Core30, Large70, etc.) | Daily | (date, code) |
| `idx_bars_daily_topix` | TOPIX OHLCV | Daily | (date) |

### Market Data Tables

| Table | Description | Update Freq | Primary Key |
|-------|-------------|-------------|-------------|
| `mkt_calendar` | Trading calendar | Yearly | (date) |
| `mkt_margin_interest` | Weekly margin trading balance | Weekly | (date, code) |
| `mkt_margin_alert` | Daily margin trading (alerted stocks) | Daily | (pub_date, code) |
| `mkt_short_ratio` | Short sale ratio by sector | Daily | (date, sector_33_code) |
| `mkt_short_sale` | Short sale position reports | Daily | (disclosure_date, code, short_seller_name) |
| `eq_investor_types` | Trading by investor type | Weekly | (pub_date, section) |

### Derivatives

| Table | Description | Update Freq | Primary Key |
|-------|-------------|-------------|-------------|
| `drv_bars_daily_opt_225` | Nikkei 225 options OHLCV + Greeks | Daily | (date, code) |

---

## Common Queries

### 1. Get Latest Stock Prices

```sql
-- Latest prices for all stocks
SELECT
    b.date,
    b.code,
    m.company_name,
    m.sector_33_name,
    b.adj_close,
    b.volume,
    b.turnover
FROM eq_bars_daily b
JOIN eq_master m USING (date, code)
WHERE b.date = (SELECT MAX(date) FROM eq_bars_daily)
ORDER BY b.turnover DESC;
```

### 2. Calculate Daily Returns

```sql
-- Daily returns for a stock
SELECT
    date,
    code,
    adj_close,
    adj_close / LAG(adj_close) OVER (ORDER BY date) - 1 AS daily_return
FROM eq_bars_daily
WHERE code = '72030'  -- Toyota
ORDER BY date DESC
LIMIT 30;
```

### 3. Calculate Moving Averages

```sql
-- 5-day and 25-day moving averages
SELECT
    date,
    code,
    adj_close,
    AVG(adj_close) OVER (ORDER BY date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS ma5,
    AVG(adj_close) OVER (ORDER BY date ROWS BETWEEN 24 PRECEDING AND CURRENT ROW) AS ma25
FROM eq_bars_daily
WHERE code = '72030'
ORDER BY date DESC
LIMIT 100;
```

### 4. Find Stocks by Sector

```sql
-- All stocks in a sector
SELECT DISTINCT
    m.code,
    m.company_name,
    m.sector_33_name,
    m.market_name
FROM eq_master m
WHERE m.date = (SELECT MAX(date) FROM eq_master)
  AND m.sector_33_code = '3050'  -- Information & Communication
ORDER BY m.company_name;
```

### 5. Get Financial Metrics (Latest)

```sql
-- Latest financials per stock
WITH latest AS (
    SELECT
        code,
        MAX(disclosure_date) AS max_date
    FROM fin_summary
    GROUP BY code
)
SELECT
    f.code,
    m.company_name,
    f.disclosure_date,
    f.sales,
    f.operating_profit,
    f.net_profit,
    f.eps,
    f.bps,
    f.equity_ratio,
    f.dividend_annual
FROM fin_summary f
JOIN latest l ON f.code = l.code AND f.disclosure_date = l.max_date
JOIN eq_master m ON f.code = m.code
    AND m.date = (SELECT MAX(date) FROM eq_master)
ORDER BY f.sales DESC NULLS LAST
LIMIT 100;
```

### 6. Calculate Valuation Ratios

```sql
-- PER, PBR, Dividend Yield
WITH latest_fins AS (
    SELECT DISTINCT ON (code)
        code,
        eps,
        bps,
        dividend_annual
    FROM fin_summary
    WHERE eps IS NOT NULL
    ORDER BY code, disclosure_date DESC
),
latest_price AS (
    SELECT
        code,
        adj_close
    FROM eq_bars_daily
    WHERE date = (SELECT MAX(date) FROM eq_bars_daily)
)
SELECT
    p.code,
    m.company_name,
    m.sector_33_name,
    p.adj_close,
    f.eps,
    f.bps,
    ROUND(p.adj_close / NULLIF(f.eps, 0), 2) AS per,
    ROUND(p.adj_close / NULLIF(f.bps, 0), 2) AS pbr,
    ROUND(f.dividend_annual / NULLIF(p.adj_close, 0) * 100, 2) AS div_yield
FROM latest_price p
JOIN latest_fins f USING (code)
JOIN eq_master m ON p.code = m.code
    AND m.date = (SELECT MAX(date) FROM eq_master)
WHERE f.eps > 0 AND f.bps > 0
ORDER BY per ASC
LIMIT 50;
```

### 7. Margin Trading Analysis

```sql
-- Margin balance and ratio
SELECT
    date,
    code,
    long_volume,
    short_volume,
    ROUND(long_volume::DOUBLE / NULLIF(short_volume, 0), 2) AS margin_ratio,
    long_volume - short_volume AS net_balance
FROM mkt_margin_interest
WHERE code = '72030'
ORDER BY date DESC
LIMIT 20;
```

### 8. Foreign Investor Flow

```sql
-- Weekly foreign investor trading
SELECT
    pub_date,
    section,
    foreign_buy / 1000000 AS foreign_buy_bil,
    foreign_sell / 1000000 AS foreign_sell_bil,
    (foreign_buy - foreign_sell) / 1000000 AS foreign_net_bil
FROM eq_investor_types
WHERE section = 'TSEPrime'
ORDER BY pub_date DESC
LIMIT 20;
```

### 9. Sector Performance

```sql
-- Sector returns over period
WITH sector_returns AS (
    SELECT
        m.sector_33_code,
        m.sector_33_name,
        b.date,
        AVG(b.adj_close / NULLIF(LAG(b.adj_close) OVER (PARTITION BY b.code ORDER BY b.date), 0) - 1) AS avg_return
    FROM eq_bars_daily b
    JOIN eq_master m USING (date, code)
    WHERE b.date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY m.sector_33_code, m.sector_33_name, b.date
)
SELECT
    sector_33_code,
    sector_33_name,
    ROUND(EXP(SUM(LN(1 + COALESCE(avg_return, 0)))) - 1, 4) AS cumulative_return
FROM sector_returns
GROUP BY sector_33_code, sector_33_name
ORDER BY cumulative_return DESC;
```

### 10. Trading Calendar

```sql
-- Check if date is trading day
SELECT
    date,
    CASE holiday_division
        WHEN '0' THEN 'Trading Day'
        WHEN '1' THEN 'Non-Trading Day'
        WHEN '2' THEN 'Holiday Trading'
        WHEN '3' THEN 'Half Day'
    END AS day_type
FROM mkt_calendar
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date;
```

---

## Feature Engineering Examples

### Daily Return Features

```sql
-- Returns at multiple horizons
SELECT
    date,
    code,
    adj_close,
    -- Daily return
    adj_close / LAG(adj_close, 1) OVER w - 1 AS ret_1d,
    -- 5-day return
    adj_close / LAG(adj_close, 5) OVER w - 1 AS ret_5d,
    -- 20-day return
    adj_close / LAG(adj_close, 20) OVER w - 1 AS ret_20d,
    -- 60-day return
    adj_close / LAG(adj_close, 60) OVER w - 1 AS ret_60d
FROM eq_bars_daily
WHERE code = '72030'
WINDOW w AS (ORDER BY date)
ORDER BY date DESC
LIMIT 100;
```

### Volatility Features

```sql
-- Rolling volatility
WITH returns AS (
    SELECT
        date,
        code,
        LN(adj_close / LAG(adj_close) OVER (PARTITION BY code ORDER BY date)) AS log_ret
    FROM eq_bars_daily
    WHERE code = '72030'
)
SELECT
    date,
    code,
    -- 20-day realized volatility (annualized)
    STDDEV(log_ret) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) * SQRT(252) AS vol_20d,
    -- 60-day realized volatility (annualized)
    STDDEV(log_ret) OVER (ORDER BY date ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) * SQRT(252) AS vol_60d
FROM returns
ORDER BY date DESC
LIMIT 100;
```

### Momentum Features

```sql
-- RSI calculation
WITH price_changes AS (
    SELECT
        date,
        code,
        adj_close - LAG(adj_close) OVER (PARTITION BY code ORDER BY date) AS change
    FROM eq_bars_daily
    WHERE code = '72030'
),
gains_losses AS (
    SELECT
        date,
        code,
        CASE WHEN change > 0 THEN change ELSE 0 END AS gain,
        CASE WHEN change < 0 THEN ABS(change) ELSE 0 END AS loss
    FROM price_changes
)
SELECT
    date,
    code,
    100 - (100 / (1 +
        AVG(gain) OVER (ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) /
        NULLIF(AVG(loss) OVER (ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW), 0)
    )) AS rsi_14
FROM gains_losses
ORDER BY date DESC
LIMIT 100;
```

### Volume Features

```sql
-- Volume-related features
SELECT
    date,
    code,
    volume,
    turnover,
    -- Volume ratio vs 20-day average
    volume::DOUBLE / NULLIF(AVG(volume) OVER (ORDER BY date ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING), 0) AS vol_ratio_20d,
    -- VWAP
    turnover / NULLIF(volume, 0) AS vwap,
    -- Price vs VWAP
    adj_close / NULLIF(turnover / NULLIF(volume, 0), 0) - 1 AS price_vs_vwap
FROM eq_bars_daily
WHERE code = '72030'
ORDER BY date DESC
LIMIT 100;
```

### Fundamental Features

```sql
-- Combined price + fundamental features
WITH latest_fins AS (
    SELECT DISTINCT ON (code)
        code,
        eps,
        bps,
        sales,
        operating_profit,
        net_profit,
        equity_ratio
    FROM fin_summary
    ORDER BY code, disclosure_date DESC
)
SELECT
    b.date,
    b.code,
    b.adj_close,
    b.turnover,
    -- Valuation
    b.adj_close / NULLIF(f.eps, 0) AS per,
    b.adj_close / NULLIF(f.bps, 0) AS pbr,
    -- Profitability
    f.operating_profit / NULLIF(f.sales, 0) AS op_margin,
    f.net_profit / NULLIF(f.sales, 0) AS net_margin,
    -- Balance sheet
    f.equity_ratio
FROM eq_bars_daily b
JOIN latest_fins f USING (code)
WHERE b.date = (SELECT MAX(date) FROM eq_bars_daily)
ORDER BY b.turnover DESC
LIMIT 100;
```

---

## Export to Parquet/CSV

```python
import duckdb

conn = duckdb.connect('data/jquants.duckdb', read_only=True)

# Export to Parquet
conn.execute("""
    COPY (
        SELECT * FROM eq_bars_daily
        WHERE date >= '2024-01-01'
    ) TO 'eq_bars_2024.parquet' (FORMAT PARQUET)
""")

# Export to CSV
conn.execute("""
    COPY (
        SELECT * FROM eq_master
        WHERE date = (SELECT MAX(date) FROM eq_master)
    ) TO 'eq_master_latest.csv' (HEADER, DELIMITER ',')
""")
```

---

## Python Integration

### With Pandas

```python
import duckdb
import pandas as pd

conn = duckdb.connect('data/jquants.duckdb', read_only=True)

# Direct to DataFrame
df = conn.execute("""
    SELECT date, code, adj_close, volume
    FROM eq_bars_daily
    WHERE code = '72030'
    ORDER BY date
""").fetchdf()

# Set index
df = df.set_index('date')
```

### With Polars

```python
import duckdb
import polars as pl

conn = duckdb.connect('data/jquants.duckdb', read_only=True)

# Direct to Polars
df = conn.execute("""
    SELECT date, code, adj_close, volume
    FROM eq_bars_daily
    WHERE code = '72030'
""").pl()
```

### Batch Processing

```python
import duckdb

conn = duckdb.connect('data/jquants.duckdb', read_only=True)

# Process in chunks
query = """
    SELECT * FROM eq_bars_daily
    WHERE date >= '2020-01-01'
"""

# Using fetchmany for memory efficiency
result = conn.execute(query)
while True:
    batch = result.fetchmany(10000)
    if not batch:
        break
    # Process batch
    print(f"Processing {len(batch)} rows...")
```

---

## Table Reference

### eq_master Columns

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Information date |
| code | VARCHAR | Stock code (5 digits) |
| company_name | VARCHAR | Company name (Japanese) |
| company_name_en | VARCHAR | Company name (English) |
| sector_17_code | VARCHAR | 17-sector code |
| sector_17_name | VARCHAR | 17-sector name |
| sector_33_code | VARCHAR | 33-sector code |
| sector_33_name | VARCHAR | 33-sector name |
| scale_category | VARCHAR | Scale category |
| market_code | VARCHAR | Market code |
| market_name | VARCHAR | Market name |
| margin_code | VARCHAR | Margin trading code |
| margin_name | VARCHAR | Margin trading name |

### eq_bars_daily Columns

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Trading date |
| code | VARCHAR | Stock code |
| open, high, low, close | DOUBLE | OHLC prices |
| volume | BIGINT | Trading volume |
| turnover | DOUBLE | Trading value |
| upper_limit, lower_limit | DOUBLE | Price limits |
| adj_factor | DOUBLE | Adjustment factor |
| adj_open, adj_high, adj_low, adj_close | DOUBLE | Adjusted prices |
| adj_volume | BIGINT | Adjusted volume |
| morning_* | DOUBLE | Morning session data |
| afternoon_* | DOUBLE | Afternoon session data |

### fin_summary Key Columns

| Column | Type | Description |
|--------|------|-------------|
| disclosure_date | DATE | Disclosure date |
| code | VARCHAR | Stock code |
| sales | DOUBLE | Revenue |
| operating_profit | DOUBLE | Operating profit |
| ordinary_profit | DOUBLE | Ordinary profit |
| net_profit | DOUBLE | Net profit |
| eps | DOUBLE | Earnings per share |
| bps | DOUBLE | Book value per share |
| equity_ratio | DOUBLE | Equity ratio (%) |
| dividend_annual | DOUBLE | Annual dividend |
| forecast_* | DOUBLE | Forecast values |

---

## Tips

1. **Use adjusted prices** (`adj_close`) for time-series analysis to account for stock splits and dividends.

2. **Join with eq_master** to get company names and sector information.

3. **Check trading calendar** before analyzing date ranges to avoid non-trading days.

4. **Use WINDOW functions** for efficient rolling calculations.

5. **Export large results to Parquet** for better compression and faster reads.
