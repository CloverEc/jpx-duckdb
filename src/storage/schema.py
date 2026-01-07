"""DuckDB schema definitions."""

from typing import Final

# Table DDL statements
SCHEMA_DDL: Final[dict[str, str]] = {
    "eq_master": """
        CREATE TABLE IF NOT EXISTS eq_master (
            date DATE,
            code VARCHAR,
            company_name VARCHAR,
            company_name_en VARCHAR,
            sector_17_code VARCHAR,
            sector_17_name VARCHAR,
            sector_33_code VARCHAR,
            sector_33_name VARCHAR,
            scale_category VARCHAR,
            market_code VARCHAR,
            market_name VARCHAR,
            margin_code VARCHAR,
            margin_name VARCHAR,
            PRIMARY KEY (date, code)
        )
    """,
    "eq_bars_daily": """
        CREATE TABLE IF NOT EXISTS eq_bars_daily (
            date DATE,
            code VARCHAR,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            upper_limit DOUBLE,
            lower_limit DOUBLE,
            volume BIGINT,
            turnover DOUBLE,
            adj_factor DOUBLE,
            adj_open DOUBLE,
            adj_high DOUBLE,
            adj_low DOUBLE,
            adj_close DOUBLE,
            adj_volume BIGINT,
            morning_open DOUBLE,
            morning_high DOUBLE,
            morning_low DOUBLE,
            morning_close DOUBLE,
            morning_upper_limit DOUBLE,
            morning_lower_limit DOUBLE,
            morning_volume BIGINT,
            morning_turnover DOUBLE,
            morning_adj_open DOUBLE,
            morning_adj_high DOUBLE,
            morning_adj_low DOUBLE,
            morning_adj_close DOUBLE,
            morning_adj_volume BIGINT,
            afternoon_open DOUBLE,
            afternoon_high DOUBLE,
            afternoon_low DOUBLE,
            afternoon_close DOUBLE,
            afternoon_upper_limit DOUBLE,
            afternoon_lower_limit DOUBLE,
            afternoon_volume BIGINT,
            afternoon_turnover DOUBLE,
            afternoon_adj_open DOUBLE,
            afternoon_adj_high DOUBLE,
            afternoon_adj_low DOUBLE,
            afternoon_adj_close DOUBLE,
            afternoon_adj_volume BIGINT,
            PRIMARY KEY (date, code)
        )
    """,
    "fin_summary": """
        CREATE TABLE IF NOT EXISTS fin_summary (
            disclosure_date DATE,
            disclosure_time VARCHAR,
            code VARCHAR,
            disclosure_no VARCHAR,
            doc_type VARCHAR,
            current_period_type VARCHAR,
            current_period_start DATE,
            current_period_end DATE,
            current_fy_start DATE,
            current_fy_end DATE,
            next_fy_start DATE,
            next_fy_end DATE,
            sales DOUBLE,
            operating_profit DOUBLE,
            ordinary_profit DOUBLE,
            net_profit DOUBLE,
            eps DOUBLE,
            diluted_eps DOUBLE,
            total_assets DOUBLE,
            equity DOUBLE,
            equity_ratio DOUBLE,
            bps DOUBLE,
            cf_operating DOUBLE,
            cf_investing DOUBLE,
            cf_financing DOUBLE,
            cash_equivalents DOUBLE,
            dividend_q1 DOUBLE,
            dividend_q2 DOUBLE,
            dividend_q3 DOUBLE,
            dividend_fy DOUBLE,
            dividend_annual DOUBLE,
            payout_ratio DOUBLE,
            forecast_sales DOUBLE,
            forecast_op DOUBLE,
            forecast_odp DOUBLE,
            forecast_np DOUBLE,
            forecast_eps DOUBLE,
            forecast_dividend_annual DOUBLE,
            next_forecast_sales DOUBLE,
            next_forecast_op DOUBLE,
            next_forecast_np DOUBLE,
            next_forecast_eps DOUBLE,
            shares_outstanding BIGINT,
            treasury_shares BIGINT,
            avg_shares BIGINT,
            nc_sales DOUBLE,
            nc_operating_profit DOUBLE,
            nc_ordinary_profit DOUBLE,
            nc_net_profit DOUBLE,
            nc_eps DOUBLE,
            nc_total_assets DOUBLE,
            nc_equity DOUBLE,
            nc_bps DOUBLE,
            PRIMARY KEY (code, disclosure_date, disclosure_no)
        )
    """,
    "eq_earnings_calendar": """
        CREATE TABLE IF NOT EXISTS eq_earnings_calendar (
            announcement_date DATE,
            code VARCHAR,
            company_name VARCHAR,
            fiscal_year_end VARCHAR,
            sector_name VARCHAR,
            fiscal_quarter VARCHAR,
            section VARCHAR,
            fetched_at TIMESTAMP,
            PRIMARY KEY (code, fiscal_year_end, fiscal_quarter)
        )
    """,
    "mkt_calendar": """
        CREATE TABLE IF NOT EXISTS mkt_calendar (
            date DATE PRIMARY KEY,
            holiday_division VARCHAR
        )
    """,
    "eq_investor_types": """
        CREATE TABLE IF NOT EXISTS eq_investor_types (
            pub_date DATE,
            start_date DATE,
            end_date DATE,
            section VARCHAR,
            proprietary_sell DOUBLE,
            proprietary_buy DOUBLE,
            proprietary_total DOUBLE,
            proprietary_balance DOUBLE,
            brokerage_sell DOUBLE,
            brokerage_buy DOUBLE,
            brokerage_total DOUBLE,
            brokerage_balance DOUBLE,
            individual_sell DOUBLE,
            individual_buy DOUBLE,
            individual_total DOUBLE,
            individual_balance DOUBLE,
            foreign_sell DOUBLE,
            foreign_buy DOUBLE,
            foreign_total DOUBLE,
            foreign_balance DOUBLE,
            securities_sell DOUBLE,
            securities_buy DOUBLE,
            securities_total DOUBLE,
            securities_balance DOUBLE,
            inv_trust_sell DOUBLE,
            inv_trust_buy DOUBLE,
            inv_trust_total DOUBLE,
            inv_trust_balance DOUBLE,
            trust_bank_sell DOUBLE,
            trust_bank_buy DOUBLE,
            trust_bank_total DOUBLE,
            trust_bank_balance DOUBLE,
            insurance_sell DOUBLE,
            insurance_buy DOUBLE,
            insurance_total DOUBLE,
            insurance_balance DOUBLE,
            bank_sell DOUBLE,
            bank_buy DOUBLE,
            bank_total DOUBLE,
            bank_balance DOUBLE,
            other_fin_sell DOUBLE,
            other_fin_buy DOUBLE,
            other_fin_total DOUBLE,
            other_fin_balance DOUBLE,
            business_sell DOUBLE,
            business_buy DOUBLE,
            business_total DOUBLE,
            business_balance DOUBLE,
            other_sell DOUBLE,
            other_buy DOUBLE,
            other_total DOUBLE,
            other_balance DOUBLE,
            total_sell DOUBLE,
            total_buy DOUBLE,
            total_total DOUBLE,
            total_balance DOUBLE,
            PRIMARY KEY (pub_date, section)
        )
    """,
    "idx_bars_daily_topix": """
        CREATE TABLE IF NOT EXISTS idx_bars_daily_topix (
            date DATE PRIMARY KEY,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE
        )
    """,
    "idx_bars_daily": """
        CREATE TABLE IF NOT EXISTS idx_bars_daily (
            date DATE,
            code VARCHAR,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            PRIMARY KEY (date, code)
        )
    """,
    "drv_bars_daily_opt_225": """
        CREATE TABLE IF NOT EXISTS drv_bars_daily_opt_225 (
            date DATE,
            code VARCHAR,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            evening_open DOUBLE,
            evening_high DOUBLE,
            evening_low DOUBLE,
            evening_close DOUBLE,
            afternoon_open DOUBLE,
            afternoon_high DOUBLE,
            afternoon_low DOUBLE,
            afternoon_close DOUBLE,
            volume BIGINT,
            open_interest BIGINT,
            turnover DOUBLE,
            contract_month VARCHAR,
            strike_price DOUBLE,
            put_call_div VARCHAR,
            last_trading_day DATE,
            sq_date DATE,
            settlement_price DOUBLE,
            theoretical_price DOUBLE,
            base_volatility DOUBLE,
            underlying_price DOUBLE,
            implied_volatility DOUBLE,
            interest_rate DOUBLE,
            PRIMARY KEY (date, code)
        )
    """,
    "mkt_margin_interest": """
        CREATE TABLE IF NOT EXISTS mkt_margin_interest (
            date DATE,
            code VARCHAR,
            short_volume BIGINT,
            long_volume BIGINT,
            short_neg_volume BIGINT,
            long_neg_volume BIGINT,
            short_std_volume BIGINT,
            long_std_volume BIGINT,
            issue_type VARCHAR,
            PRIMARY KEY (date, code)
        )
    """,
    "mkt_short_ratio": """
        CREATE TABLE IF NOT EXISTS mkt_short_ratio (
            date DATE,
            sector_33_code VARCHAR,
            sell_ex_short_value DOUBLE,
            short_with_restriction_value DOUBLE,
            short_no_restriction_value DOUBLE,
            PRIMARY KEY (date, sector_33_code)
        )
    """,
    "mkt_short_sale": """
        CREATE TABLE IF NOT EXISTS mkt_short_sale (
            disclosure_date DATE,
            calculation_date DATE,
            code VARCHAR,
            short_seller_name VARCHAR,
            short_seller_address VARCHAR,
            dic_name VARCHAR,
            dic_address VARCHAR,
            fund_name VARCHAR,
            short_position_ratio DOUBLE,
            short_position_shares BIGINT,
            short_position_units BIGINT,
            prev_report_date DATE,
            prev_report_ratio DOUBLE,
            notes VARCHAR,
            PRIMARY KEY (disclosure_date, code, short_seller_name)
        )
    """,
    "mkt_margin_alert": """
        CREATE TABLE IF NOT EXISTS mkt_margin_alert (
            pub_date DATE,
            code VARCHAR,
            app_date DATE,
            pub_reason VARCHAR,
            short_outstanding BIGINT,
            short_outstanding_change BIGINT,
            short_outstanding_ratio VARCHAR,
            long_outstanding BIGINT,
            long_outstanding_change BIGINT,
            long_outstanding_ratio VARCHAR,
            sl_ratio DOUBLE,
            short_neg_outstanding BIGINT,
            short_neg_outstanding_change BIGINT,
            short_std_outstanding BIGINT,
            short_std_outstanding_change BIGINT,
            long_neg_outstanding BIGINT,
            long_neg_outstanding_change BIGINT,
            long_std_outstanding BIGINT,
            long_std_outstanding_change BIGINT,
            tse_margin_reg_class VARCHAR,
            PRIMARY KEY (pub_date, code)
        )
    """,
    "sync_metadata": """
        CREATE TABLE IF NOT EXISTS sync_metadata (
            table_name VARCHAR PRIMARY KEY,
            last_sync_date DATE,
            last_sync_timestamp TIMESTAMP,
            records_synced BIGINT,
            status VARCHAR
        )
    """,
    "sync_log": """
        CREATE SEQUENCE IF NOT EXISTS sync_log_seq START 1;
        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER DEFAULT nextval('sync_log_seq') PRIMARY KEY,
            table_name VARCHAR,
            sync_date DATE,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            records_fetched BIGINT,
            records_inserted BIGINT,
            records_updated BIGINT,
            status VARCHAR,
            error_message VARCHAR
        )
    """,
}

# Index DDL statements
INDEX_DDL: Final[dict[str, list[str]]] = {
    "eq_bars_daily": [
        "CREATE INDEX IF NOT EXISTS idx_eq_bars_code ON eq_bars_daily(code)",
        "CREATE INDEX IF NOT EXISTS idx_eq_bars_date ON eq_bars_daily(date)",
    ],
    "fin_summary": [
        "CREATE INDEX IF NOT EXISTS idx_fin_summary_code ON fin_summary(code)",
        "CREATE INDEX IF NOT EXISTS idx_fin_summary_date ON fin_summary(disclosure_date)",
    ],
    "idx_bars_daily": [
        "CREATE INDEX IF NOT EXISTS idx_idx_bars_code ON idx_bars_daily(code)",
    ],
    "mkt_margin_interest": [
        "CREATE INDEX IF NOT EXISTS idx_margin_code ON mkt_margin_interest(code)",
    ],
    "sync_log": [
        "CREATE INDEX IF NOT EXISTS idx_sync_log_table ON sync_log(table_name)",
        "CREATE INDEX IF NOT EXISTS idx_sync_log_date ON sync_log(sync_date)",
    ],
}

# All table names in order
TABLE_NAMES: Final[list[str]] = [
    "eq_master",
    "eq_bars_daily",
    "fin_summary",
    "eq_earnings_calendar",
    "mkt_calendar",
    "eq_investor_types",
    "idx_bars_daily_topix",
    "idx_bars_daily",
    "drv_bars_daily_opt_225",
    "mkt_margin_interest",
    "mkt_short_ratio",
    "mkt_short_sale",
    "mkt_margin_alert",
    "sync_metadata",
    "sync_log",
]


def create_all_tables(conn: "duckdb.DuckDBPyConnection") -> None:  # noqa: F821
    """Create all tables and indexes.

    Args:
        conn: DuckDB connection
    """
    import duckdb

    # Create tables
    for table_name in TABLE_NAMES:
        ddl = SCHEMA_DDL[table_name]
        for statement in ddl.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(statement)

    # Create indexes
    for table_name, indexes in INDEX_DDL.items():
        for index_ddl in indexes:
            conn.execute(index_ddl)

    # Initialize sync_metadata
    conn.execute("""
        INSERT OR IGNORE INTO sync_metadata (table_name, status)
        SELECT unnest(?), 'pending'
    """, [[t for t in TABLE_NAMES if t not in ("sync_metadata", "sync_log")]])
