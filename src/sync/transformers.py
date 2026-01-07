"""Data transformers for API responses to database records."""

from datetime import datetime
from typing import Any

from src.utils.date import parse_date


def safe_float(val: Any) -> float | None:
    """Convert value to float, handling empty strings."""
    if val is None or val == "" or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_int(val: Any) -> int | None:
    """Convert value to int, handling empty strings."""
    if val is None or val == "" or val == "":
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def safe_date(val: str | None) -> Any:
    """Convert value to date, handling empty strings and invalid values."""
    if val is None or val == "" or val == "-":
        return None
    try:
        return parse_date(val)
    except (ValueError, TypeError):
        return None


def transform_eq_master(record: dict[str, Any]) -> dict[str, Any]:
    """Transform eq-master API response to database record."""
    return {
        "date": parse_date(record["Date"]),
        "code": record["Code"],
        "company_name": record.get("CoName"),
        "company_name_en": record.get("CoNameEn"),
        "sector_17_code": record.get("S17"),
        "sector_17_name": record.get("S17Nm"),
        "sector_33_code": record.get("S33"),
        "sector_33_name": record.get("S33Nm"),
        "scale_category": record.get("ScaleCat"),
        "market_code": record.get("Mkt"),
        "market_name": record.get("MktNm"),
        "margin_code": record.get("Mrgn"),
        "margin_name": record.get("MrgnNm"),
    }


def transform_eq_bars_daily(record: dict[str, Any]) -> dict[str, Any]:
    """Transform eq-bars-daily API response to database record."""
    return {
        "date": parse_date(record["Date"]),
        "code": record["Code"],
        "open": safe_float(record.get("O")),
        "high": safe_float(record.get("H")),
        "low": safe_float(record.get("L")),
        "close": safe_float(record.get("C")),
        "upper_limit": safe_float(record.get("UL")),
        "lower_limit": safe_float(record.get("LL")),
        "volume": safe_float(record.get("Vo")),
        "turnover": safe_float(record.get("Va")),
        "adj_factor": safe_float(record.get("AdjFactor")),
        "adj_open": safe_float(record.get("AdjO")),
        "adj_high": safe_float(record.get("AdjH")),
        "adj_low": safe_float(record.get("AdjL")),
        "adj_close": safe_float(record.get("AdjC")),
        "adj_volume": safe_float(record.get("AdjVo")),
        "morning_open": safe_float(record.get("MO")),
        "morning_high": safe_float(record.get("MH")),
        "morning_low": safe_float(record.get("ML")),
        "morning_close": safe_float(record.get("MC")),
        "morning_upper_limit": safe_float(record.get("MUL")),
        "morning_lower_limit": safe_float(record.get("MLL")),
        "morning_volume": safe_float(record.get("MVo")),
        "morning_turnover": safe_float(record.get("MVa")),
        "morning_adj_open": safe_float(record.get("MAdjO")),
        "morning_adj_high": safe_float(record.get("MAdjH")),
        "morning_adj_low": safe_float(record.get("MAdjL")),
        "morning_adj_close": safe_float(record.get("MAdjC")),
        "morning_adj_volume": safe_float(record.get("MAdjVo")),
        "afternoon_open": safe_float(record.get("AO")),
        "afternoon_high": safe_float(record.get("AH")),
        "afternoon_low": safe_float(record.get("AL")),
        "afternoon_close": safe_float(record.get("AC")),
        "afternoon_upper_limit": safe_float(record.get("AUL")),
        "afternoon_lower_limit": safe_float(record.get("ALL")),
        "afternoon_volume": safe_float(record.get("AVo")),
        "afternoon_turnover": safe_float(record.get("AVa")),
        "afternoon_adj_open": safe_float(record.get("AAdjO")),
        "afternoon_adj_high": safe_float(record.get("AAdjH")),
        "afternoon_adj_low": safe_float(record.get("AAdjL")),
        "afternoon_adj_close": safe_float(record.get("AAdjC")),
        "afternoon_adj_volume": safe_float(record.get("AAdjVo")),
    }


def transform_fin_summary(record: dict[str, Any]) -> dict[str, Any]:
    """Transform fin-summary API response to database record."""
    return {
        "disclosure_date": parse_date(record["DiscDate"]),
        "disclosure_time": record.get("DiscTime") or None,
        "code": record["Code"],
        "disclosure_no": record.get("DiscNo") or None,
        "doc_type": record.get("DocType") or None,
        "current_period_type": record.get("CurPerType") or None,
        "current_period_start": safe_date(record.get("CurPerSt")),
        "current_period_end": safe_date(record.get("CurPerEn")),
        "current_fy_start": safe_date(record.get("CurFYSt")),
        "current_fy_end": safe_date(record.get("CurFYEn")),
        "next_fy_start": safe_date(record.get("NxtFYSt")),
        "next_fy_end": safe_date(record.get("NxtFYEn")),
        "sales": safe_float(record.get("Sales")),
        "operating_profit": safe_float(record.get("OP")),
        "ordinary_profit": safe_float(record.get("OdP")),
        "net_profit": safe_float(record.get("NP")),
        "eps": safe_float(record.get("EPS")),
        "diluted_eps": safe_float(record.get("DEPS")),
        "total_assets": safe_float(record.get("TA")),
        "equity": safe_float(record.get("Eq")),
        "equity_ratio": safe_float(record.get("EqAR")),
        "bps": safe_float(record.get("BPS")),
        "cf_operating": safe_float(record.get("CFO")),
        "cf_investing": safe_float(record.get("CFI")),
        "cf_financing": safe_float(record.get("CFF")),
        "cash_equivalents": safe_float(record.get("CashEq")),
        "dividend_q1": safe_float(record.get("Div1Q")),
        "dividend_q2": safe_float(record.get("Div2Q")),
        "dividend_q3": safe_float(record.get("Div3Q")),
        "dividend_fy": safe_float(record.get("DivFY")),
        "dividend_annual": safe_float(record.get("DivAnn")),
        "payout_ratio": safe_float(record.get("PayoutRatioAnn")),
        "forecast_sales": safe_float(record.get("FSales")),
        "forecast_op": safe_float(record.get("FOP")),
        "forecast_odp": safe_float(record.get("FOdP")),
        "forecast_np": safe_float(record.get("FNP")),
        "forecast_eps": safe_float(record.get("FEPS")),
        "forecast_dividend_annual": safe_float(record.get("FDivAnn")),
        "next_forecast_sales": safe_float(record.get("NxFSales")),
        "next_forecast_op": safe_float(record.get("NxFOP")),
        "next_forecast_np": safe_float(record.get("NxFNp")),
        "next_forecast_eps": safe_float(record.get("NxFEPS")),
        "shares_outstanding": safe_float(record.get("ShOutFY")),
        "treasury_shares": safe_float(record.get("TrShFY")),
        "avg_shares": safe_float(record.get("AvgSh")),
        "nc_sales": safe_float(record.get("NCSales")),
        "nc_operating_profit": safe_float(record.get("NCOP")),
        "nc_ordinary_profit": safe_float(record.get("NCOdP")),
        "nc_net_profit": safe_float(record.get("NCNP")),
        "nc_eps": safe_float(record.get("NCEPS")),
        "nc_total_assets": safe_float(record.get("NCTA")),
        "nc_equity": safe_float(record.get("NCEq")),
        "nc_bps": safe_float(record.get("NCBPS")),
    }


def transform_eq_earnings_calendar(record: dict[str, Any]) -> dict[str, Any]:
    """Transform eq-earnings-calendar API response to database record."""
    return {
        "announcement_date": parse_date(record["Date"]),
        "code": record["Code"],
        "company_name": record.get("CoName"),
        "fiscal_year_end": record.get("FY"),
        "sector_name": record.get("SectorNm"),
        "fiscal_quarter": record.get("FQ"),
        "section": record.get("Section"),
        "fetched_at": datetime.now(),
    }


def transform_mkt_calendar(record: dict[str, Any]) -> dict[str, Any]:
    """Transform mkt-calendar API response to database record."""
    return {
        "date": parse_date(record["Date"]),
        "holiday_division": record.get("HolDiv"),
    }


def transform_eq_investor_types(record: dict[str, Any]) -> dict[str, Any]:
    """Transform eq-investor-types API response to database record."""
    return {
        "pub_date": parse_date(record["PubDate"]),
        "start_date": parse_date(record["StDate"]),
        "end_date": parse_date(record["EnDate"]),
        "section": record.get("Section") or None,
        "proprietary_sell": safe_float(record.get("PropSell")),
        "proprietary_buy": safe_float(record.get("PropBuy")),
        "proprietary_total": safe_float(record.get("PropTot")),
        "proprietary_balance": safe_float(record.get("PropBal")),
        "brokerage_sell": safe_float(record.get("BrkSell")),
        "brokerage_buy": safe_float(record.get("BrkBuy")),
        "brokerage_total": safe_float(record.get("BrkTot")),
        "brokerage_balance": safe_float(record.get("BrkBal")),
        "individual_sell": safe_float(record.get("IndSell")),
        "individual_buy": safe_float(record.get("IndBuy")),
        "individual_total": safe_float(record.get("IndTot")),
        "individual_balance": safe_float(record.get("IndBal")),
        "foreign_sell": safe_float(record.get("FrgnSell")),
        "foreign_buy": safe_float(record.get("FrgnBuy")),
        "foreign_total": safe_float(record.get("FrgnTot")),
        "foreign_balance": safe_float(record.get("FrgnBal")),
        "securities_sell": safe_float(record.get("SecCoSell")),
        "securities_buy": safe_float(record.get("SecCoBuy")),
        "securities_total": safe_float(record.get("SecCoTot")),
        "securities_balance": safe_float(record.get("SecCoBal")),
        "inv_trust_sell": safe_float(record.get("InvTrSell")),
        "inv_trust_buy": safe_float(record.get("InvTrBuy")),
        "inv_trust_total": safe_float(record.get("InvTrTot")),
        "inv_trust_balance": safe_float(record.get("InvTrBal")),
        "trust_bank_sell": safe_float(record.get("TrstBnkSell")),
        "trust_bank_buy": safe_float(record.get("TrstBnkBuy")),
        "trust_bank_total": safe_float(record.get("TrstBnkTot")),
        "trust_bank_balance": safe_float(record.get("TrstBnkBal")),
        "insurance_sell": safe_float(record.get("InsCoSell")),
        "insurance_buy": safe_float(record.get("InsCoBuy")),
        "insurance_total": safe_float(record.get("InsCoTot")),
        "insurance_balance": safe_float(record.get("InsCoBal")),
        "bank_sell": safe_float(record.get("BankSell")),
        "bank_buy": safe_float(record.get("BankBuy")),
        "bank_total": safe_float(record.get("BankTot")),
        "bank_balance": safe_float(record.get("BankBal")),
        "other_fin_sell": safe_float(record.get("OthFinSell")),
        "other_fin_buy": safe_float(record.get("OthFinBuy")),
        "other_fin_total": safe_float(record.get("OthFinTot")),
        "other_fin_balance": safe_float(record.get("OthFinBal")),
        "business_sell": safe_float(record.get("BusCoSell")),
        "business_buy": safe_float(record.get("BusCoBuy")),
        "business_total": safe_float(record.get("BusCoTot")),
        "business_balance": safe_float(record.get("BusCoBal")),
        "other_sell": safe_float(record.get("OthSell")),
        "other_buy": safe_float(record.get("OthBuy")),
        "other_total": safe_float(record.get("OthTot")),
        "other_balance": safe_float(record.get("OthBal")),
        "total_sell": safe_float(record.get("TotSell")),
        "total_buy": safe_float(record.get("TotBuy")),
        "total_total": safe_float(record.get("TotTot")),
        "total_balance": safe_float(record.get("TotBal")),
    }


def transform_idx_bars_daily_topix(record: dict[str, Any]) -> dict[str, Any]:
    """Transform idx-bars-daily-topix API response to database record."""
    return {
        "date": parse_date(record["Date"]),
        "open": safe_float(record.get("O")),
        "high": safe_float(record.get("H")),
        "low": safe_float(record.get("L")),
        "close": safe_float(record.get("C")),
    }


def transform_idx_bars_daily(record: dict[str, Any]) -> dict[str, Any]:
    """Transform idx-bars-daily API response to database record."""
    return {
        "date": parse_date(record["Date"]),
        "code": record["Code"],
        "open": safe_float(record.get("O")),
        "high": safe_float(record.get("H")),
        "low": safe_float(record.get("L")),
        "close": safe_float(record.get("C")),
    }


def transform_drv_bars_daily_opt_225(record: dict[str, Any]) -> dict[str, Any]:
    """Transform drv-bars-daily-opt-225 API response to database record."""
    return {
        "date": parse_date(record["Date"]),
        "code": record["Code"],
        "open": safe_float(record.get("O")),
        "high": safe_float(record.get("H")),
        "low": safe_float(record.get("L")),
        "close": safe_float(record.get("C")),
        "evening_open": safe_float(record.get("EO")),
        "evening_high": safe_float(record.get("EH")),
        "evening_low": safe_float(record.get("EL")),
        "evening_close": safe_float(record.get("EC")),
        "afternoon_open": safe_float(record.get("AO")),
        "afternoon_high": safe_float(record.get("AH")),
        "afternoon_low": safe_float(record.get("AL")),
        "afternoon_close": safe_float(record.get("AC")),
        "volume": safe_float(record.get("Vo")),
        "open_interest": safe_float(record.get("OI")),
        "turnover": safe_float(record.get("Va")),
        "contract_month": record.get("CM") or None,
        "strike_price": safe_float(record.get("Strike")),
        "put_call_div": record.get("PCDiv") or None,
        "last_trading_day": safe_date(record.get("LTD")),
        "sq_date": safe_date(record.get("SQD")),
        "settlement_price": safe_float(record.get("Settle")),
        "theoretical_price": safe_float(record.get("Theo")),
        "base_volatility": safe_float(record.get("BaseVol")),
        "underlying_price": safe_float(record.get("UnderPx")),
        "implied_volatility": safe_float(record.get("IV")),
        "interest_rate": safe_float(record.get("IR")),
    }


def transform_mkt_margin_interest(record: dict[str, Any]) -> dict[str, Any]:
    """Transform mkt-margin-int API response to database record."""
    return {
        "date": parse_date(record["Date"]),
        "code": record["Code"],
        "short_volume": safe_float(record.get("ShrtVol")),
        "long_volume": safe_float(record.get("LongVol")),
        "short_neg_volume": safe_float(record.get("ShrtNegVol")),
        "long_neg_volume": safe_float(record.get("LongNegVol")),
        "short_std_volume": safe_float(record.get("ShrtStdVol")),
        "long_std_volume": safe_float(record.get("LongStdVol")),
        "issue_type": record.get("IssType") or None,
    }


def transform_mkt_short_ratio(record: dict[str, Any]) -> dict[str, Any]:
    """Transform mkt-short-ratio API response to database record."""
    return {
        "date": parse_date(record["Date"]),
        "sector_33_code": record.get("S33") or None,
        "sell_ex_short_value": safe_float(record.get("SellExShortVa")),
        "short_with_restriction_value": safe_float(record.get("ShrtWithResVa")),
        "short_no_restriction_value": safe_float(record.get("ShrtNoResVa")),
    }


def transform_mkt_short_sale(record: dict[str, Any]) -> dict[str, Any]:
    """Transform mkt-short-sale API response to database record."""
    return {
        "disclosure_date": parse_date(record["DiscDate"]),
        "calculation_date": safe_date(record.get("CalcDate")),
        "code": record["Code"],
        "short_seller_name": record.get("SSName") or None,
        "short_seller_address": record.get("SSAddr") or None,
        "dic_name": record.get("DICName") or None,
        "dic_address": record.get("DICAddr") or None,
        "fund_name": record.get("FundName") or None,
        "short_position_ratio": safe_float(record.get("ShrtPosToSO")),
        "short_position_shares": safe_float(record.get("ShrtPosShares")),
        "short_position_units": safe_float(record.get("ShrtPosUnits")),
        "prev_report_date": safe_date(record.get("PrevRptDate")),
        "prev_report_ratio": safe_float(record.get("PrevRptRatio")),
        "notes": record.get("Notes") or None,
    }


def transform_mkt_margin_alert(record: dict[str, Any]) -> dict[str, Any]:
    """Transform mkt-margin-alert API response to database record."""
    pub_reason = record.get("PubReason")
    if isinstance(pub_reason, dict):
        pub_reason = str(pub_reason)
    elif pub_reason == "":
        pub_reason = None

    return {
        "pub_date": parse_date(record["PubDate"]),
        "code": record["Code"],
        "app_date": safe_date(record.get("AppDate")),
        "pub_reason": pub_reason,
        "short_outstanding": safe_float(record.get("ShrtOut")),
        "short_outstanding_change": safe_float(record.get("ShrtOutChg")),
        "short_outstanding_ratio": record.get("ShrtOutRatio") or None,
        "long_outstanding": safe_float(record.get("LongOut")),
        "long_outstanding_change": safe_float(record.get("LongOutChg")),
        "long_outstanding_ratio": safe_float(record.get("LongOutRatio")),
        "sl_ratio": safe_float(record.get("SLRatio")),
        "short_neg_outstanding": safe_float(record.get("ShrtNegOut")),
        "short_neg_outstanding_change": safe_float(record.get("ShrtNegOutChg")),
        "short_std_outstanding": safe_float(record.get("ShrtStdOut")),
        "short_std_outstanding_change": safe_float(record.get("ShrtStdOutChg")),
        "long_neg_outstanding": safe_float(record.get("LongNegOut")),
        "long_neg_outstanding_change": safe_float(record.get("LongNegOutChg")),
        "long_std_outstanding": safe_float(record.get("LongStdOut")),
        "long_std_outstanding_change": safe_float(record.get("LongStdOutChg")),
        "tse_margin_reg_class": record.get("TSEMrgnRegCls") or None,
    }


# Transformer mapping
TRANSFORMERS = {
    "eq_master": transform_eq_master,
    "eq_bars_daily": transform_eq_bars_daily,
    "fin_summary": transform_fin_summary,
    "eq_earnings_calendar": transform_eq_earnings_calendar,
    "mkt_calendar": transform_mkt_calendar,
    "eq_investor_types": transform_eq_investor_types,
    "idx_bars_daily_topix": transform_idx_bars_daily_topix,
    "idx_bars_daily": transform_idx_bars_daily,
    "drv_bars_daily_opt_225": transform_drv_bars_daily_opt_225,
    "mkt_margin_interest": transform_mkt_margin_interest,
    "mkt_short_ratio": transform_mkt_short_ratio,
    "mkt_short_sale": transform_mkt_short_sale,
    "mkt_margin_alert": transform_mkt_margin_alert,
}
