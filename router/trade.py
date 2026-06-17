from fastapi import APIRouter, Depends
from db import get_db
from router.auth import get_current_user

router = APIRouter(prefix="/api/trades", tags=["trades"])

# ✅ トレード登録（API）
@router.post("/")
def create_trade(
    stock_code: str,
    buy_date: str,
    buy_price: float,
    sell_date: str,
    sell_price: float,
    memo: str = "",
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

    db.commit()

    return {"status": "ok"}


# ✅ 一覧（API）
@router.get("/")
def get_trades(
    db = Depends(get_db),
    user_id = Depends(get_current_user)
):
    cursor = db.cursor()

    cursor.execute("""
    SELECT * FROM trades WHERE user_id = ?
    ORDER BY id DESC
    """, (user_id,))

    results = cursor.fetchall()

    return [dict(row) for row in results]

@router.post("/delete/{trade_id}")
def delete_trade(
    trade_id: int,
    db = Depends(get_db),
    user_id = Depends(get_current_user)
):

    cursor = db.cursor()

    # ✅ 自分のデータだけ削除（重要）
    cursor.execute("""
    DELETE FROM trades
    WHERE id = ? AND user_id = ?
    """, (trade_id, user_id))

    db.commit()

    return {"status": "deleted"}
    db = Depends(get_db),
    user_id = Depends(get_current_user)
    cursor = db.cursor()



