from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from db import get_db
from router.auth import get_current_user
from typing import List

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
