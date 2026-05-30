from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import yfinance as yf
import sqlite3

# ルーター読み込み
from router.auth import router as auth_router, get_current_user
from router.stock import router as stock_router
from router.favorites import router as favorites_router


# ================================
#  DB 初期化
# ================================
import bcrypt

hashed = bcrypt.hashpw("password".encode(), bcrypt.gensalt())

conn = sqlite3.connect("stocks.db")
cursor = conn.cursor()

cursor.execute("""
    INSERT OR IGNORE INTO users (username, password)
    VALUES (?, ?)
""", ("admin", hashed))

conn.commit()
conn.close()

# ================================
#  FastAPI アプリ本体
# ================================
app = FastAPI()

# ルーター登録
app.include_router(auth_router)
app.include_router(stock_router)
app.include_router(favorites_router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================================
#  ホーム画面
# ================================
@app.get("/")
def home(request: Request, user_id: int = Depends(get_current_user)):
    indices = {
        "日経平均": "^N225",
        "NYダウ": "^DJI",
        "NASDAQ": "^IXIC",
        "S&P500": "^GSPC",
        "TOPIX": "^TOPX"
    }

    results = []
    for name, code in indices.items():
        try:
            stock = yf.Ticker(code)

            price = stock.info.get("regularMarketPrice")
            prev_close = stock.info.get("previousClose")

            # fallback
            if price is None:
                hist = stock.history(period="2d")
                if not hist.empty:
                    price = hist["Close"].iloc[-1]
                    prev_close = hist["Close"].iloc[-2]

            # 前日比計算
            if price and prev_close:
                diff = price - prev_close
                diff_percent = (diff / prev_close) * 100
            else:
                diff = None
                diff_percent = None

            results.append({
                "name": name,
                "code": code,
                "price": price,
                "diff": diff,
                "diff_percent": diff_percent
            })

        except Exception:
            results.append({
                "name": name,
                "code": code,
                "price": "N/A",
                "diff": None,
                "diff_percent": None
            })

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user_id, "indices": results}
    )

