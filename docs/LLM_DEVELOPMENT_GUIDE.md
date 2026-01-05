# LLM Development Guide for jpx-duckdb

## Overview

This document serves as the primary reference for LLM-assisted development of the jpx-duckdb project. It contains all necessary information about J-Quants API v2 endpoints (Standard Plan) and development policies.

---

## Development Policy

### 1. Code Style

- **Language**: Python 3.11+
- **Type Hints**: Required for all functions
- **Docstrings**: Google style
- **Formatter**: Black (line-length=100)
- **Linter**: Ruff
- **Import Sort**: isort

### 2. Architecture Principles

- **Single Responsibility**: Each module handles one endpoint or one concern
- **DRY**: Common logic in base classes (rate limiting, pagination, retry)
- **Fail Fast**: Validate inputs early, raise clear exceptions
- **Idempotency**: Re-running sync should not create duplicates (UPSERT)

### 3. Error Handling

```python
# Standard error handling pattern
try:
    response = await client.get(url, params=params)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        # Rate limit - exponential backoff
        await asyncio.sleep(backoff_time)
        return await retry_request(...)
    elif e.response.status_code == 401:
        raise AuthenticationError("Invalid API key")
    else:
        raise APIError(f"HTTP {e.response.status_code}: {e.response.text}")
```

### 4. Rate Limiting Strategy

- Default: 1 request per second
- On 429: Exponential backoff (1s, 2s, 4s, 8s, max 60s)
- Use semaphore for concurrent requests (max 3)
- Log all rate limit events

### 5. Data Validation

- Validate API responses against expected schema
- Log warnings for unexpected fields (don't fail)
- Fail on missing required fields

### 6. Testing Requirements

- Unit tests for all data transformations
- Integration tests with mock API responses
- End-to-end tests for critical sync paths

---

## J-Quants API v2 Endpoints (Standard Plan)

### Available Endpoints Summary

| # | Endpoint | Japanese Name | Path | Update Frequency |
|---|----------|--------------|------|------------------|
| 1 | eq-master | 上場銘柄一覧 | /equities/master | Daily 17:30 |
| 2 | eq-bars-daily | 株価四本値 | /equities/bars/daily | Daily 16:30 |
| 3 | fin-summary | 財務情報 | /fins/summary | Daily 18:00/24:30 |
| 4 | eq-earnings-cal | 決算発表予定日 | /equities/earnings-calendar | Irregular 19:00 |
| 5 | mkt-cal | 取引カレンダー | /markets/calendar | Yearly |
| 6 | eq-investor-types | 投資部門別情報 | /equities/investor-types | Weekly Thu 18:00 |
| 7 | idx-bars-daily-topix | TOPIX四本値 | /indices/bars/daily/topix | Daily 16:30 |
| 8 | idx-bars-daily | 指数四本値 | /indices/bars/daily | Daily 16:30 |
| 9 | drv-bars-daily-opt-225 | 日経225オプション四本値 | /derivatives/bars/daily/options/225 | Daily 27:00 |
| 10 | mkt-margin-int | 信用取引週末残高 | /markets/margin-interest | Weekly Tue 16:30 |
| 11 | mkt-short-ratio | 業種別空売り比率 | /markets/short-ratio | Daily 16:30 |
| 12 | mkt-short-sale | 空売り残高報告 | /markets/short-sale-report | Daily 17:30 |
| 13 | mkt-margin-alert | 日々公表信用取引残高 | /markets/margin-alert | Daily 16:30 |

---

## Endpoint Specifications

### 1. eq-master (上場銘柄一覧)

Listed issue information with sector and market classification.

**Path**: `GET /equities/master`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| code | String | No | 5-digit stock code (e.g., 27800) |
| date | String | No | Date (YYYYMMDD or YYYY-MM-DD) |
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| Date | String | 情報適用日 (YYYY-MM-DD) |
| Code | String | 銘柄コード |
| CoName | String | 会社名 |
| CoNameEn | String | 会社名(英語) |
| S17 | String | 17業種コード |
| S17Nm | String | 17業種コード名 |
| S33 | String | 33業種コード |
| S33Nm | String | 33業種コード名 |
| ScaleCat | String | 規模コード |
| Mkt | String | 市場コード |
| MktNm | String | 市場コード名 |
| Mrgn | String | 信用コード |
| MrgnNm | String | 信用コード名 |

**Request Patterns**:
- `[]` - All stocks for current date
- `[code]` - Specific stock for current date
- `[date]` - All stocks for specific date
- `[code, date]` - Specific stock for specific date

---

### 2. eq-bars-daily (株価四本値)

Daily OHLCV stock price data with adjusted prices.

**Path**: `GET /equities/bars/daily`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| code | String | No* | 5-digit stock code |
| date | String | No* | Date (YYYYMMDD or YYYY-MM-DD) |
| from | String | No | Start date |
| to | String | No | End date |
| pagination_key | String | No | Pagination key |

*Either code or date is required

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| Date | String | 取引日 |
| Code | String | 銘柄コード |
| O | Number | 始値 |
| H | Number | 高値 |
| L | Number | 安値 |
| C | Number | 終値 |
| UL | Number | 上限値 |
| LL | Number | 下限値 |
| Vo | Number | 出来高 |
| Va | Number | 売買代金 |
| AdjFactor | Number | 調整係数 |
| AdjO | Number | 調整後始値 |
| AdjH | Number | 調整後高値 |
| AdjL | Number | 調整後安値 |
| AdjC | Number | 調整後終値 |
| AdjVo | Number | 調整後出来高 |
| MO | Number | 前場始値 |
| MH | Number | 前場高値 |
| ML | Number | 前場安値 |
| MC | Number | 前場終値 |
| MUL | Number | 前場上限値 |
| MLL | Number | 前場下限値 |
| MVo | Number | 前場出来高 |
| MVa | Number | 前場売買代金 |
| MAdjO | Number | 前場調整後始値 |
| MAdjH | Number | 前場調整後高値 |
| MAdjL | Number | 前場調整後安値 |
| MAdjC | Number | 前場調整後終値 |
| MAdjVo | Number | 前場調整後出来高 |
| AO | Number | 後場始値 |
| AH | Number | 後場高値 |
| AL | Number | 後場安値 |
| AC | Number | 後場終値 |
| AUL | Number | 後場上限値 |
| ALL | Number | 後場下限値 |
| AVo | Number | 後場出来高 |
| AVa | Number | 後場売買代金 |
| AAdjO | Number | 後場調整後始値 |
| AAdjH | Number | 後場調整後高値 |
| AAdjL | Number | 後場調整後安値 |
| AAdjC | Number | 後場調整後終値 |
| AAdjVo | Number | 後場調整後出来高 |

**Request Patterns**:
- `[code]` - All data for specific stock
- `[code, date]` - Specific stock on specific date
- `[code, from, to]` - Specific stock in date range
- `[date]` - All stocks on specific date

---

### 3. fin-summary (財務情報)

Quarterly financial statements.

**Path**: `GET /fins/summary`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| code | String | No* | 5-digit stock code |
| date | String | No* | Disclosure date (YYYY-MM-DD or YYYYMMDD) |
| pagination_key | String | No | Pagination key |

*Either code or date is required

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| DiscDate | String | 開示日 |
| DiscTime | String | 開示時間 |
| Code | String | 銘柄コード |
| DiscNo | String | 開示番号 |
| DocType | String | 開示書類の種類 |
| CurPerType | String | 現在の期間 |
| CurPerSt | String | 現在の期間の開始日 |
| CurPerEn | String | 現在の期間の終了日 |
| CurFYSt | String | 現在の会計年度の開始日 |
| CurFYEn | String | 現在の会計年度の終了日 |
| NxtFYSt | String | 次の会計年度の開始日 |
| NxtFYEn | String | 次の会計年度の終了日 |
| Sales | Number | 売上高 |
| OP | Number | 営業利益 |
| OdP | Number | 経常利益 |
| NP | Number | 当期純利益 |
| EPS | Number | 1株当たり利益(EPS) |
| DEPS | Number | 希薄化後EPS |
| TA | Number | 総資産 |
| Eq | Number | 純資産 |
| EqAR | Number | 純資産比率 |
| BPS | Number | 1株当たり簿価 |
| CFO | Number | 営業キャッシュフロー |
| CFI | Number | 投資キャッシュフロー |
| CFF | Number | 財政キャッシュフロー |
| CashEq | Number | 現金及び当座預金 |
| Div1Q | Number | 第1四半期の配当金 |
| Div2Q | Number | 第2四半期の配当金 |
| Div3Q | Number | 第3四半期の配当金 |
| DivFY | Number | 期末の配当金 |
| DivAnn | Number | 年間の配当金 |
| PayoutRatioAnn | Number | 年間の配当性向 |
| FSales | Number | 予想売上高 |
| FOP | Number | 予想営業利益 |
| FOdP | Number | 予想経常利益 |
| FNP | Number | 予想当期純利益 |
| FEPS | Number | 予想EPS |
| FDivAnn | Number | 予想年間配当金 |
| NxFSales | Number | 次年度予想売上高 |
| NxFOP | Number | 次年度予想営業利益 |
| NxFNp | Number | 次年度予想当期純利益 |
| NxFEPS | Number | 次年度予想EPS |
| ShOutFY | Number | 発行済株式数 |
| TrShFY | Number | 自己株式数 |
| AvgSh | Number | 平均発行株式数 |
| NCSales | Number | 単体売上高 |
| NCOP | Number | 単体営業利益 |
| NCOdP | Number | 単体経常利益 |
| NCNP | Number | 単体当期純利益 |
| NCEPS | Number | 単体EPS |
| NCTA | Number | 単体総資産 |
| NCEq | Number | 単体純資産 |
| NCBPS | Number | 単体BPS |

---

### 4. eq-earnings-cal (決算発表予定日)

Earnings announcement calendar.

**Path**: `GET /equities/earnings-calendar`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| Date | String | 発表予定日 (YYYY-MM-DD) |
| Code | String | 銘柄コード |
| CoName | String | 会社名 |
| FY | String | 決算期末 |
| SectorNm | String | 業種名 |
| FQ | String | 決算種類 |
| Section | String | 市場区分 |

**Note**: Returns next day's scheduled announcements. Only covers March/September fiscal year companies. Excludes REITs.

---

### 5. mkt-cal (取引カレンダー)

Trading calendar for TSE and OSE.

**Path**: `GET /markets/calendar`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| hol_div | String | No | Holiday division code |
| from | String | No | Start date |
| to | String | No | End date |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| Date | String | 日付 (YYYY-MM-DD) |
| HolDiv | String | 祝日区分コード |

**Holiday Division Codes**:
- `0`: 営業日 (Business day)
- `1`: 休業日 (Non-business day)
- `2`: 祝日取引日 (Holiday trading day)
- `3`: 非営業日（半日立会） (Half-day trading)

---

### 6. eq-investor-types (投資部門別情報)

Trading by type of investors (weekly).

**Path**: `GET /equities/investor-types`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| section | String | No | Market section (e.g., TSEPrime) |
| from | String | No | Start date |
| to | String | No | End date |
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| PubDate | String | 公表日 |
| StDate | String | 開始日 |
| EnDate | String | 終了日 |
| Section | String | 市場名 |
| PropSell | Number | 自己売却額（千円） |
| PropBuy | Number | 自己買付額（千円） |
| PropTot | Number | 自己売買代金（千円） |
| PropBal | Number | 自己残高（千円） |
| BrkSell | Number | 委託売却額（千円） |
| BrkBuy | Number | 委託買付額（千円） |
| IndSell | Number | 個人売却額（千円） |
| IndBuy | Number | 個人買付額（千円） |
| FrgnSell | Number | 外国人売却額（千円） |
| FrgnBuy | Number | 外国人買付額（千円） |
| SecCoSell | Number | 証券会社売却額（千円） |
| SecCoBuy | Number | 証券会社買付額（千円） |
| InvTrSell | Number | 投資信託売却額（千円） |
| InvTrBuy | Number | 投資信託買付額（千円） |
| TrstBnkSell | Number | 信託銀行売却額（千円） |
| TrstBnkBuy | Number | 信託銀行買付額（千円） |
| InsCoSell | Number | 保険会社売却額（千円） |
| InsCoBuy | Number | 保険会社買付額（千円） |
| BankSell | Number | 銀行売却額（千円） |
| BankBuy | Number | 銀行買付額（千円） |
| OthFinSell | Number | その他金融機関売却額（千円） |
| OthFinBuy | Number | その他金融機関買付額（千円） |
| BusCoSell | Number | 商業銀行売却額（千円） |
| BusCoBuy | Number | 商業銀行買付額（千円） |
| TotSell | Number | 売買代金（千円） |
| TotBuy | Number | 買買代金（千円） |

---

### 7. idx-bars-daily-topix (TOPIX四本値)

TOPIX index OHLC data.

**Path**: `GET /indices/bars/daily/topix`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| from | String | No | Start date |
| to | String | No | End date |
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| Date | String | 取引日 (YYYY-MM-DD) |
| O | Number | 始値 |
| H | Number | 高値 |
| L | Number | 安値 |
| C | Number | 終値 |

---

### 8. idx-bars-daily (指数四本値)

Index OHLC data for various indices (TOPIX Core30, Large70, Growth Market 250, etc.).

**Path**: `GET /indices/bars/daily`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| code | String | No | Index code |
| date | String | No | Date |
| from | String | No | Start date |
| to | String | No | End date |
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| Date | String | 取引日 (YYYY-MM-DD) |
| Code | String | 指数コード |
| O | Number | 始値 |
| H | Number | 高値 |
| L | Number | 安値 |
| C | Number | 終値 |

---

### 9. drv-bars-daily-opt-225 (日経225オプション四本値)

Nikkei 225 options OHLC and Greeks.

**Path**: `GET /derivatives/bars/daily/options/225`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| date | String | **Yes** | Date (YYYYMMDD or YYYY-MM-DD) |
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| Date | String | 取引日 |
| Code | String | 証券コード |
| O | Number | 全日始値 |
| H | Number | 全日高値 |
| L | Number | 全日安値 |
| C | Number | 全日終値 |
| EO | Number | 夜間始値 |
| EH | Number | 夜間高値 |
| EL | Number | 夜間安値 |
| EC | Number | 夜間終値 |
| AO | Number | 日中始値 |
| AH | Number | 日中高値 |
| AL | Number | 日中安値 |
| AC | Number | 日中終値 |
| Vo | Number | 出来高 |
| OI | Number | 建玉 |
| Va | Number | 売買代金 |
| CM | String | 限月 (YYYY-MM) |
| Strike | Number | 権利行使価格 |
| PCDiv | String | プット/コール区分 (1:プット, 2:コール) |
| LTD | String | 最終取引日 |
| SQD | String | 特別清算日 |
| Settle | Number | 清算値段 |
| Theo | Number | 理論価格 |
| BaseVol | Number | 基準変動率 |
| UnderPx | Number | 原資産価格 |
| IV | Number | 暗示的変動率 (Implied Volatility) |
| IR | Number | 金利 |

---

### 10. mkt-margin-int (信用取引週末残高)

Weekly margin trading outstanding (end of week).

**Path**: `GET /markets/margin-interest`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| code | String | No | 5-digit stock code |
| from | String | No | Start date |
| to | String | No | End date |
| date | String | No | Specific date |
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| Date | String | 申込日付 (YYYY-MM-DD) |
| Code | String | 銘柄コード |
| ShrtVol | Number | 売合計信用取引週末残高 |
| LongVol | Number | 買合計信用取引週末残高 |
| ShrtNegVol | Number | 売一般信用取引週末残高 |
| LongNegVol | Number | 買一般信用取引週末残高 |
| ShrtStdVol | Number | 売制度信用取引週末残高 |
| LongStdVol | Number | 買制度信用取引週末残高 |
| IssType | String | 銘柄区分 (1:信用銘柄, 2:貸借銘柄, 3:その他) |

---

### 11. mkt-short-ratio (業種別空売り比率)

Short sale value and ratio by sector (33 sectors).

**Path**: `GET /markets/short-ratio`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| s33 | String | No | 33-sector code (e.g., 0050) |
| from | String | No | Start date |
| to | String | No | End date |
| date | String | No | Specific date |
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| Date | String | 取引日 (YYYY-MM-DD) |
| S33 | String | 33業種コード |
| SellExShortVa | Number | 通常売り注文の売買代金 |
| ShrtWithResVa | Number | 価格規制付き空売りの売買代金 |
| ShrtNoResVa | Number | 価格規制なし空売りの売買代金 |

---

### 12. mkt-short-sale (空売り残高報告)

Outstanding short selling positions reported by large holders.

**Path**: `GET /markets/short-sale-report`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| code | String | No | 5-digit stock code |
| disc_date | String | No | Disclosure date |
| disc_date_from | String | No | Disclosure date start |
| disc_date_to | String | No | Disclosure date end |
| calc_date | String | No | Calculation date |
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| DiscDate | String | 開示日 (YYYY-MM-DD) |
| CalcDate | String | 算出日 (YYYY-MM-DD) |
| Code | String | 銘柄コード |
| SSName | String | 空売り者名 |
| SSAddr | String | 空売り者住所 |
| DICName | String | 裁量投資顧問名 |
| DICAddr | String | 裁量投資顧問住所 |
| FundName | String | 投資信託名 |
| ShrtPosToSO | Number | 空売り残高の発行済株式総数に対する比率 |
| ShrtPosShares | Number | 空売り残高の株数 |
| ShrtPosUnits | Number | 空売り残高の単元株数 |
| PrevRptDate | String | 前回開示日 |
| PrevRptRatio | Number | 前回開示日の比率 |
| Notes | String | 備考 |

---

### 13. mkt-margin-alert (日々公表信用取引残高)

Daily margin trading outstanding for stocks subject to daily publication.

**Path**: `GET /markets/margin-alert`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| code | String | No | 5-digit stock code |
| from | String | No | Start date |
| to | String | No | End date |
| date | String | No | Specific date |
| pagination_key | String | No | Pagination key |

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| PubDate | String | 公表日 (YYYY-MM-DD) |
| Code | String | 銘柄コード |
| AppDate | String | 申込日 (YYYY-MM-DD) |
| PubReason | Map | 公表理由 |
| ShrtOut | Number | 信用売り残高合計 |
| ShrtOutChg | Number | 信用売り残高の前日比 |
| ShrtOutRatio | String | 信用売り残高の発行済株式数に対する比率 |
| LongOut | Number | 信用買い残高合計 |
| LongOutChg | Number | 信用買い残高の前日比 |
| LongOutRatio | String | 信用買い残高の発行済株式数に対する比率 |
| SLRatio | Number | 信用倍率（買残÷売残） |
| ShrtNegOut | Number | 一般信用取引売残高 |
| ShrtNegOutChg | Number | 一般信用取引売残高の前日比 |
| ShrtStdOut | Number | 制度信用取引売残高 |
| ShrtStdOutChg | Number | 制度信用取引売残高の前日比 |
| LongNegOut | Number | 一般信用取引買残高 |
| LongNegOutChg | Number | 一般信用取引買残高の前日比 |
| LongStdOut | Number | 制度信用取引買残高 |
| LongStdOutChg | Number | 制度信用取引買残高の前日比 |
| TSEMrgnRegCls | String | 東証信用貸借規制区分 |

---

## DuckDB Schema (Complete)

### Tables Required

```sql
-- 1. eq_master (上場銘柄一覧)
CREATE TABLE eq_master (
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
);

-- 2. eq_bars_daily (株価四本値)
CREATE TABLE eq_bars_daily (
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
);

-- 3. fin_summary (財務情報)
CREATE TABLE fin_summary (
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
);

-- 4. eq_earnings_calendar (決算発表予定日)
CREATE TABLE eq_earnings_calendar (
    announcement_date DATE,
    code VARCHAR,
    company_name VARCHAR,
    fiscal_year_end VARCHAR,
    sector_name VARCHAR,
    fiscal_quarter VARCHAR,
    section VARCHAR,
    fetched_at TIMESTAMP,
    PRIMARY KEY (code, fiscal_year_end, fiscal_quarter)
);

-- 5. mkt_calendar (取引カレンダー)
CREATE TABLE mkt_calendar (
    date DATE PRIMARY KEY,
    holiday_division VARCHAR
);

-- 6. eq_investor_types (投資部門別情報)
CREATE TABLE eq_investor_types (
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
);

-- 7. idx_bars_daily_topix (TOPIX四本値)
CREATE TABLE idx_bars_daily_topix (
    date DATE PRIMARY KEY,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE
);

-- 8. idx_bars_daily (指数四本値)
CREATE TABLE idx_bars_daily (
    date DATE,
    code VARCHAR,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    PRIMARY KEY (date, code)
);

-- 9. drv_bars_daily_opt_225 (日経225オプション四本値)
CREATE TABLE drv_bars_daily_opt_225 (
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
);

-- 10. mkt_margin_interest (信用取引週末残高)
CREATE TABLE mkt_margin_interest (
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
);

-- 11. mkt_short_ratio (業種別空売り比率)
CREATE TABLE mkt_short_ratio (
    date DATE,
    sector_33_code VARCHAR,
    sell_ex_short_value DOUBLE,
    short_with_restriction_value DOUBLE,
    short_no_restriction_value DOUBLE,
    PRIMARY KEY (date, sector_33_code)
);

-- 12. mkt_short_sale (空売り残高報告)
CREATE TABLE mkt_short_sale (
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
);

-- 13. mkt_margin_alert (日々公表信用取引残高)
CREATE TABLE mkt_margin_alert (
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
);

-- Metadata tables
CREATE TABLE sync_metadata (
    table_name VARCHAR PRIMARY KEY,
    last_sync_date DATE,
    last_sync_timestamp TIMESTAMP,
    records_synced BIGINT,
    status VARCHAR
);

CREATE SEQUENCE IF NOT EXISTS sync_log_seq START 1;
CREATE TABLE sync_log (
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
);
```

---

## Sync Schedule

| Table | Schedule | Time | Note |
|-------|----------|------|------|
| eq_master | Daily | 18:00 | After 17:30 update |
| eq_bars_daily | Daily | 17:00 | After 16:30 update |
| fin_summary | Daily | 19:00 + 01:00 | Speed + Final |
| eq_earnings_calendar | Daily | 20:00 | After 19:00 update |
| mkt_calendar | Monthly | 1st 09:00 | Rarely changes |
| eq_investor_types | Weekly | Thu 19:00 | After 18:00 update |
| idx_bars_daily_topix | Daily | 17:00 | After 16:30 update |
| idx_bars_daily | Daily | 17:00 | After 16:30 update |
| drv_bars_daily_opt_225 | Daily | 04:00 | After 27:00 (03:00) update |
| mkt_margin_interest | Weekly | Tue 17:00 | After 16:30 update |
| mkt_short_ratio | Daily | 17:00 | After 16:30 update |
| mkt_short_sale | Daily | 18:00 | After 17:30 update |
| mkt_margin_alert | Daily | 17:00 | After 16:30 update |

---

## File Structure

```
jpx-duckdb/
├── README.md
├── LLM_DEVELOPMENT_GUIDE.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── client/
│   │   ├── __init__.py
│   │   ├── base.py              # Base client with rate limiting
│   │   ├── equities.py          # eq-master, eq-bars-daily
│   │   ├── financials.py        # fin-summary, eq-earnings-cal
│   │   ├── indices.py           # idx-bars-daily, idx-bars-daily-topix
│   │   ├── derivatives.py       # drv-bars-daily-opt-225
│   │   └── markets.py           # mkt-* endpoints
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── duckdb.py            # DuckDB operations
│   │   ├── schema.py            # DDL definitions
│   │   └── parquet.py           # Parquet export
│   ├── sync/
│   │   ├── __init__.py
│   │   ├── initial.py           # Initial full load
│   │   ├── daily.py             # Daily sync
│   │   └── weekly.py            # Weekly sync
│   └── utils/
│       ├── __init__.py
│       ├── date.py              # Date utilities
│       └── logging.py           # Logging configuration
├── scripts/
│   ├── init_db.py               # Initialize database
│   ├── sync_all.py              # Run all syncs
│   └── export_parquet.py        # Export to Parquet
├── tests/
│   ├── __init__.py
│   ├── test_client/
│   ├── test_storage/
│   └── test_sync/
└── docs/
    ├── duckdb_schema.md
    └── api_reference.md
```

---

## Environment Variables

```bash
# .env.example
JQUANTS_API_KEY=your_api_key_here
DUCKDB_PATH=./data/jquants.duckdb
LOG_LEVEL=INFO
RATE_LIMIT_RPS=1
MAX_RETRIES=3
BACKOFF_FACTOR=2
```

---

## Usage Examples

### Initial Load (10 years)

```python
from src.sync.initial import InitialLoader

loader = InitialLoader()
await loader.load_all(years=10)
```

### Daily Sync

```python
from src.sync.daily import DailySync

sync = DailySync()
await sync.run()
```

### Query Data

```python
import duckdb

conn = duckdb.connect('data/jquants.duckdb')

# Get latest prices with returns
result = conn.execute("""
    SELECT
        date, code, adj_close,
        adj_close / LAG(adj_close) OVER (PARTITION BY code ORDER BY date) - 1 as return
    FROM eq_bars_daily
    WHERE code = '72030'
    ORDER BY date DESC
    LIMIT 10
""").fetchdf()
```
