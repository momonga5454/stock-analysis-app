from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import yfinance as yf
import sqlite3
import os
import bcrypt


# ルーター
from router.auth import router as auth_router, get_current_user
from router.stock import router as stock_router
from router.favorites import router as favorites_router
from init_db import init_db
from router.data import router as data_router
from router.trade import router as trade_router
from router.trade_view import router as trade_view_router
from router.tag import router as tag_router

# ================================
# DB 初期化
# ================================
init_db()

# ================================
# FastAPI
# ================================
app = FastAPI()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "stock.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# favorites
cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    code TEXT,
    name TEXT,
    UNIQUE(user_id, code)
)
""")

# admin作成
hashed = bcrypt.hashpw("password".encode(), bcrypt.gensalt())

cursor.execute("""
INSERT OR IGNORE INTO users (username, password)
VALUES (?, ?)
""", ("admin", hashed))

conn.commit()
conn.close()

# ================================
# FastAPI
# ================================
app = FastAPI()

app.include_router(auth_router)
app.include_router(stock_router)
app.include_router(favorites_router)
app.include_router(data_router)
app.include_router(trade_router)
app.include_router(trade_view_router)
app.include_router(tag_router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================================
# ホーム
# ================================
@app.get("/")
def home(request: Request, user_id: int = Depends(get_current_user)):
    indices = {
        "日経平均": "^N225",
        "NYダウ": "^DJI",
        "NASDAQ": "^IXIC",
        "S&P500": "^GSPC",
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
                if len(hist) >= 2:
                    price = hist["Close"].iloc[-1]
                    prev_close = hist["Close"].iloc[-2]

            # 差分計算
            if price is not None and prev_close is not None and prev_close != 0:
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

        except:
            results.append({
                "name": name,
                "code": code,
                "price": None,
                "diff": None,
                "diff_percent": None
            })

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user_id,
            "indices": results
        }
    )

@app.exception_handler(HTTPException)
def auth_exception_handler(request, exc):
    if exc.status_code == 401:
        return RedirectResponse("/login")
    return RedirectResponse("/")
