import pandas as pd
from db import get_conn


def run_backtest(
    symbol: str,
    hold_days: int = 1,
    start: str = None,
    end: str = None
):

    db = get_conn()

    df = pd.read_sql_query("""
    SELECT * FROM prices
    WHERE stock_code = ?
    ORDER BY date
    """, db, params=(symbol,))

    
    if start:
        df = df[df["date"] >= start]

    if end:
        df = df[df["date"] <= end]

    # 指標計算（そのまま）
    df["return"] = (
        df["open"].shift(-hold_days) - df["open"]
    ) / df["open"]


    db.close()

    if df.empty:
        return {"status": "error"}

    # 保有日数ベースのリターン
    df["return"] = (
        df["open"].shift(-hold_days) - df["open"]
    ) / df["open"]

    df = df.dropna()

    win_rate = float((df["return"] > 0).mean())
    avg_return = float(df["return"].mean())

    cum = (1 + df["return"]).cumprod()
    peak = cum.cummax()
    drawdown = (cum - peak) / peak
    max_dd = float(drawdown.min())

    losing = (df["return"] < 0).astype(int)
    max_losing_streak = int(
        losing.groupby((losing != losing.shift()).cumsum()).sum().max()
    )

    return {
        "hold_days": hold_days,
        "win_rate": win_rate,
        "avg_return": avg_return,
        "max_drawdown": max_dd,
        "max_losing_streak": max_losing_streak,
        "trades": len(df)
    }