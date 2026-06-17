import yfinance as yf
from db import get_conn
import pandas as pd

def fetch_and_save_prices(symbol: str, period="4y"):

    db = get_conn()
    cursor = db.cursor()

    df = yf.download(symbol, period=period)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty:
        return {"status": "error"}

    for index, row in df.iterrows():

        open_price = float(row["Open"].item() if hasattr(row["Open"], "item") else row["Open"])
        high_price = float(row["High"].item() if hasattr(row["High"], "item") else row["High"])
        low_price = float(row["Low"].item() if hasattr(row["Low"], "item") else row["Low"])
        close_price = float(row["Close"].item() if hasattr(row["Close"], "item") else row["Close"])

        cursor.execute("""
        INSERT OR IGNORE INTO prices
        (stock_code, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol,
            str(index.date()),
            open_price,
            high_price,
            low_price,
            close_price,
            float(row["Volume"])
        ))

    db.commit()
    db.close()

    return {"status": "ok", "rows": len(df)}