"""
Searcher Sample: 特徴量作成サンプル

このスクリプトは、jpx-duckdbからデータを取得し、特徴量を作成するサンプルです。

目的:
    - DuckDBから株価データを取得
    - テクニカル特徴量を生成（5つ）
    - シンプルなモデルで訓練・評価

対象ユーザー:
    jpx-ls-searcher等の別リポジトリから、このDBを利用するサーチャー（研究者）

DBパス設定:
    - jpx-ls-searcherから使う場合: "../../jpx-duckdb/data/jquants.duckdb"
    - このリポジトリ内から使う場合: "../data/jquants.duckdb"

Usage:
    python searcher_sample.py
"""

import duckdb
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score


# =============================================================================
# 設定
# =============================================================================

# DBパス（環境に応じて調整）
DB_PATH = Path(__file__).parent / "../data/jquants.duckdb"

# 期間設定
START_DATE = "2020-01-01"
END_DATE = "2024-12-31"
TRAIN_END = "2023-12-31"  # これ以前 = 訓練、これより後 = テスト

# 特徴量リスト
FEATURES = [
    "ret_1",      # 1日リターン
    "ret_5",      # 5日リターン
    "ret_20",     # 20日リターン
    "vol_20",     # 20日ボラティリティ
    "turn_ratio", # 出来高比率（20日平均比）
]


# =============================================================================
# リーク防止について（重要）
# =============================================================================
"""
時系列データでは「未来の情報を使わない」ことが必須です。

■ 訓練/テスト分割
─────────────────────────────────────────────────►時間
|<──── 訓練期間 ────>|<── テスト期間 ──>|
     2020-01-01      2023-12-31  2024-01-01    2024-12-31
                          ↑
                     ここで区切る（未来データは訓練に使わない）

■ 特徴量とターゲット
 T-20  T-5  T-1   T    T+1
  │    │    │    │     │
  ▼    ▼    ▼    ▼     ▼
[過去データ] → [特徴量] → [予測対象]

・ret_1  : T-1 → T の変化率（T終値で確定 → 使用OK）
・target : T → T+1 の変化率（T+1終値が必要 → 予測対象）

■ 注意点
- 特徴量は「当日終値時点で確定している情報」のみ使用
- ターゲット（翌日リターン）は予測対象なので特徴量に含めない
- 財務データ（EPS等）はdisclosure_date以降のみ使用可能
"""


# =============================================================================
# データ取得
# =============================================================================

def load_price_data(
    db_path: str | Path,
    start_date: str,
    end_date: str,
    codes: list[str] | None = None
) -> pd.DataFrame:
    """
    DuckDBから株価データを取得

    Args:
        db_path: DuckDBファイルパス
        start_date: 開始日 (YYYY-MM-DD)
        end_date: 終了日 (YYYY-MM-DD)
        codes: 銘柄コードリスト（Noneで全銘柄）

    Returns:
        DataFrame: Date, Code, Open, High, Low, Close, Volume
    """
    conn = duckdb.connect(str(db_path), read_only=True)

    query = """
        SELECT
            b.date AS Date,
            b.code AS Code,
            b.adj_open AS Open,
            b.adj_high AS High,
            b.adj_low AS Low,
            b.adj_close AS Close,
            b.adj_volume AS Volume
        FROM eq_bars_daily b
        WHERE b.date BETWEEN ? AND ?
          AND b.adj_close IS NOT NULL
          AND b.adj_volume > 0
    """

    params = [start_date, end_date]

    if codes:
        placeholders = ", ".join(["?" for _ in codes])
        query += f" AND b.code IN ({placeholders})"
        params.extend(codes)

    query += " ORDER BY b.date, b.code"

    df = conn.execute(query, params).fetchdf()
    conn.close()

    return df


# =============================================================================
# 特徴量生成
# =============================================================================

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    テクニカル特徴量を生成

    生成する特徴量:
        - ret_1: 1日リターン (T-1 → T)
        - ret_5: 5日リターン (T-5 → T)
        - ret_20: 20日リターン (T-20 → T)
        - vol_20: 20日ボラティリティ
        - turn_ratio: 出来高比率（20日平均比）

    ターゲット:
        - target: 翌日リターン (T → T+1)

    Args:
        df: Date, Code, Open, High, Low, Close, Volume を含むDataFrame

    Returns:
        DataFrame: 特徴量とターゲットを追加したDataFrame
    """
    df = df.copy()
    df = df.sort_values(["Code", "Date"]).reset_index(drop=True)

    grp = df.groupby("Code")

    # === 特徴量（当日終値時点で確定） ===

    # リターン系
    df["ret_1"] = grp["Close"].pct_change(1)    # 1日リターン
    df["ret_5"] = grp["Close"].pct_change(5)    # 5日リターン
    df["ret_20"] = grp["Close"].pct_change(20)  # 20日リターン

    # ボラティリティ（20日間の日次リターンの標準偏差）
    df["vol_20"] = grp["ret_1"].transform(
        lambda x: x.rolling(20, min_periods=20).std()
    )

    # 出来高比率（当日出来高 / 20日平均出来高）
    df["vol_ma_20"] = grp["Volume"].transform(
        lambda x: x.rolling(20, min_periods=20).mean()
    )
    df["turn_ratio"] = df["Volume"] / df["vol_ma_20"]
    df = df.drop(columns=["vol_ma_20"])

    # === ターゲット（翌日リターン） ===
    # shift(-1) で翌日の終値を持ってくる
    df["target"] = grp["Close"].shift(-1) / df["Close"] - 1

    return df


# =============================================================================
# モデル訓練
# =============================================================================

def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    alpha: float = 1.0
) -> Ridge:
    """
    Ridge回帰モデルを訓練

    Args:
        X_train: 訓練特徴量
        y_train: 訓練ターゲット
        alpha: 正則化パラメータ

    Returns:
        Ridge: 訓練済みモデル
    """
    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train)
    return model


def evaluate_model(
    model: Ridge,
    X: pd.DataFrame,
    y: pd.Series,
    label: str = ""
) -> dict:
    """
    モデルを評価

    Args:
        model: 訓練済みモデル
        X: 特徴量
        y: ターゲット
        label: 表示用ラベル

    Returns:
        dict: 評価指標
    """
    y_pred = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)

    if label:
        print(f"=== {label} ===")
        print(f"  RMSE: {rmse:.6f}")
        print(f"  R2:   {r2:.6f}")

    return {"rmse": rmse, "r2": r2, "predictions": y_pred}


# =============================================================================
# メイン処理
# =============================================================================

def main():
    print("=" * 60)
    print("Searcher Sample: 特徴量作成サンプル")
    print("=" * 60)

    # --- 1. データ取得 ---
    print("\n[1] Loading data...")
    print(f"    DB: {DB_PATH.resolve()}")
    print(f"    Period: {START_DATE} ~ {END_DATE}")

    df = load_price_data(
        db_path=DB_PATH,
        start_date=START_DATE,
        end_date=END_DATE
    )

    print(f"    Shape: {df.shape}")
    print(f"    Stocks: {df['Code'].nunique()}")

    # --- 2. 特徴量生成 ---
    print("\n[2] Generating features...")

    df = generate_features(df)

    print(f"    Features: {FEATURES}")
    for f in FEATURES:
        valid_count = df[f].notna().sum()
        print(f"      {f}: {valid_count:,} valid rows")

    # --- 3. 訓練/テスト分割 ---
    print("\n[3] Splitting train/test...")
    print(f"    Train end: {TRAIN_END}")

    # 欠損値を除去
    df_clean = df.dropna(subset=FEATURES + ["target"])

    # 時間で分割
    train_df = df_clean[df_clean["Date"] <= TRAIN_END]
    test_df = df_clean[df_clean["Date"] > TRAIN_END]

    print(f"    Train: {train_df['Date'].min()} ~ {train_df['Date'].max()} ({len(train_df):,} rows)")
    print(f"    Test:  {test_df['Date'].min()} ~ {test_df['Date'].max()} ({len(test_df):,} rows)")

    # 特徴量とターゲットを分離
    X_train = train_df[FEATURES]
    y_train = train_df["target"]
    X_test = test_df[FEATURES]
    y_test = test_df["target"]

    # --- 4. モデル訓練 ---
    print("\n[4] Training model...")

    model = train_model(X_train, y_train)

    print("    Model: Ridge(alpha=1.0)")
    print("    Feature coefficients:")
    for name, coef in zip(FEATURES, model.coef_):
        print(f"      {name}: {coef:.6f}")

    # --- 5. 評価 ---
    print("\n[5] Evaluating...")

    evaluate_model(model, X_train, y_train, label="Train")
    evaluate_model(model, X_test, y_test, label="Test")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
