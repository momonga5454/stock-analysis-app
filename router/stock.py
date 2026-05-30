# stock.py
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
import yfinance as yf
import mplfinance as mpf
import os
from router.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/stock")
def stock(request: Request, code: str, user: str = Depends(get_current_user)):
    message = ""
    img_path = None

    try:
        stock = yf.Ticker(code)
        company_name = stock.info.get("longName", code)
        data = stock.history(period="3mo")

        if data.empty:
            message = "銘柄コードが存在しないか、データを取得できません。"
        else:
            os.makedirs("static", exist_ok=True)
            img_path = f"static/{code}.png"

            mpf.plot(
                data,
                type="candle",
                mav=(5, 25),
                volume=True,
                title=company_name + " Stock Price",
                style="yahoo",
                savefig=img_path
            )

            message = f"{company_name} のチャートを表示します。"

    except Exception as e:
        message = f"エラーが発生しました: {e}"

    return templates.TemplateResponse(
        "stock.html",
        {"request": request, "message": message, "img_path": img_path, "code": code}
    )
