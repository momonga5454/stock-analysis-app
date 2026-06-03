from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import yfinance as yf
from router.auth import get_current_user, verify_csrf
from db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ================================
#  お気に入り追加
# ================================
@router.post("/favorite")
def add_favorite(
    request: Request,
    code: str = Form(...),
    csrf_token: str = Form(...),
    user_id: int = Depends(get_current_user),
    conn = Depends(get_db)
):
    verify_csrf(request, csrf_token)

    cursor = conn.cursor()

    stock = yf.Ticker(code)
    info = stock.info
    name = info.get("longName") or code

    cursor.execute(
        "SELECT id FROM favorites WHERE code = ? AND user_id = ?",
        (code, user_id)
    )
    exists = cursor.fetchone()

    if exists:
        cursor.execute(
            "UPDATE favorites SET name = ? WHERE code = ? AND user_id = ?",
            (name, code, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO favorites (code, name, user_id) VALUES (?, ?, ?)",
            (code, name, user_id)
        )

    conn.commit()

    return {"status": "ok"}


# ================================
#  お気に入り削除
# ================================
@router.post("/delete_favorite")
def delete_favorite(
    request: Request,
    code: str = Form(...),
    csrf_token: str = Form(...),
    user_id: int = Depends(get_current_user),
    conn = Depends(get_db)
):
    verify_csrf(request, csrf_token)

    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM favorites WHERE code = ? AND user_id = ?",
        (code, user_id)
    )
    conn.commit()

    return RedirectResponse("/favorites", status_code=302)


# ================================
#  お気に入り一覧
# ================================
@router.get("/favorites")
def show_favorites(
    request: Request,
    user_id: int = Depends(get_current_user),
    conn = Depends(get_db)
):
    cursor = conn.cursor()

    # ✅ ここ修正（超重要）
    cursor.execute(
        "SELECT code, name FROM favorites WHERE user_id = ?",
        (user_id,)
    )

    favorites = cursor.fetchall()

    return templates.TemplateResponse(
        "favorites.html",
        {"request": request, "favorites": favorites}
    )



