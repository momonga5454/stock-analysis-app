from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from db import get_db
from router.auth import get_current_user
from typing import List
from services.tag_analysis import analyze_tags
from services.tag_analysis import analyze_tag_combinations
from services.price_service import fetch_and_save_prices
from services.backtest import run_backtest

router = APIRouter(tags=["trade-view"])

templates = Jinja2Templates(directory="templates")

# ✅ 入力画面
@router.get("/trade")
def trade_page(
    request: Request,
    db = Depends(get_db),
    user_id = Depends(get_current_user)
):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM tags")
    tags = cursor.fetchall()

    return templates.TemplateResponse("trade.html", {
        "request": request,
        "tags": tags
    })


# ✅ フォーム送信
@router.post("/trade")
def create_trade_form(
    request: Request,
    stock_code: str = Form(...),
    buy_date: str = Form(...),
    buy_price: float = Form(...),
    sell_date: str = Form(...),
    sell_price: float = Form(...),
    memo: str = Form(""),
    tag_ids: List[int] = Form([]),
    new_tags: List[str] = Form([]),
    db = Depends(get_db),
    user_id = Depends(get_current_user)
):
    cursor = db.cursor()

    profit = (sell_price - buy_price) / buy_price

    cursor.execute("""
    INSERT INTO trades
    (user_id, stock_code, buy_date, buy_price, sell_date, sell_price, profit, memo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        stock_code,
        buy_date,
        buy_price,
        sell_date,
        sell_price,
        profit,
        memo
    ))

    trade_id = cursor.lastrowid

    # ✅ 新しいタグがあれば追加
    for new_tag in new_tags:
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (new_tag,))
    
        # 作ったタグID取得
        cursor.execute("SELECT id FROM tags WHERE name = ?", (new_tag,))
        new_tag_id = cursor.fetchone()[0]
        tag_ids.append(new_tag_id)

    for tag_id in tag_ids:
        cursor.execute("""
        INSERT INTO taggings (trade_id, tag_id)
        VALUES (?, ?)
        """, (trade_id, tag_id))

    db.commit()

    # ✅ 登録後は一覧へ
    return RedirectResponse(url="/trades", status_code=303)


# ✅ 一覧画面
@router.get("/trades")
def trades_page(
    request: Request,
    db = Depends(get_db),
    user_id = Depends(get_current_user)
):
    cursor = db.cursor()

    cursor.execute("""
    SELECT * FROM trades WHERE user_id = ?
    ORDER BY id DESC
    """, (user_id,))

    trades = cursor.fetchall()

    return templates.TemplateResponse("trades.html", {
        "request": request,
        "trades": trades
    })


@router.post("/trade/delete/{trade_id}")
def delete_trade_form(
    trade_id: int,
    db = Depends(get_db),
    user_id = Depends(get_current_user)
):
    cursor = db.cursor()

    cursor.execute("""
    DELETE FROM trades
    WHERE id = ? AND user_id = ?
    """, (trade_id, user_id))

    db.commit()

    return RedirectResponse(url="/trades", status_code=303)


@router.get("/tag-analysis")
def tag_analysis_page(
    request: Request,
    user_id = Depends(get_current_user)
):
    results = analyze_tags(user_id)

    return templates.TemplateResponse("tag_analysis.html", {
        "request": request,
        "results": results
    })


@router.get("/tag-combo-analysis")
def tag_combo_page(
    request: Request,
    user_id=Depends(get_current_user)
):
    results = analyze_tag_combinations(user_id)

    return templates.TemplateResponse("tag_combo_analysis.html", {
        "request": request,
        "results": results
    })

@router.get("/backtest")
@router.get("/backtest-ui")
def backtest_ui(request: Request):
    return templates.TemplateResponse("backtest.html", {
        "request": request,
        "result": None
    })


@router.post("/backtest")
def run_backtest_form(
    request: Request,
    symbol: str = Form(...),
    start: str = Form(...),
    end: str = Form(...),
    hold_days: int = Form(...),
    user_id=Depends(get_current_user)
):
    symbol = symbol.upper()

    if symbol.isdigit():
        symbol += ".T"

    fetch_result = fetch_and_save_prices(symbol)
    result = run_backtest(symbol, hold_days, start, end)

    return templates.TemplateResponse("backtest.html", {
        "request": request,
        "symbol": symbol,
        "start": start,
        "end": end,
        "hold_days": hold_days,
        "fetch_result": fetch_result,
        "result": result
    })
