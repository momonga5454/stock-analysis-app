import os
import time
import yfinance as yf
import mplfinance as mpf

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

CACHE_DIR = "static/charts"
CACHE_EXPIRE = 60 * 3

os.makedirs(CACHE_DIR, exist_ok=True)


@router.get("/stock")
@router.post("/stock")
def show_stock(
    request: Request,
    code: str = Form(None),
    ma_short: int = Form(5),
    ma_long: int = Form(25)
):

    # ------------------------
    # GET の場合
    # ------------------------
    if request.method == "GET":
        code = request.query_params.get("code")

        ma_short_q = request.query_params.get("ma_short")
        ma_long_q = request.query_params.get("ma_long")

        ma_short = int(ma_short_q) if ma_short_q and ma_short_q.isdigit() else 5
        ma_long = int(ma_long_q) if ma_long_q and ma_long_q.isdigit() else 25

    # ------------------------
    # MAを整数化
    # ------------------------
    try:
        ma_short = int(ma_short)
        ma_long = int(ma_long)
    except:
        ma_short = 5
        ma_long = 25

    # ------------------------
    # 銘柄コード未入力
    # ------------------------
    if not code:
        return templates.TemplateResponse(
            "stock.html",
            {
                "request": request,
                "message": "銘柄コードを入力してください",
                "img_path": None,
                "ma_short": ma_short,
                "ma_long": ma_long,
                "code": ""
            }
        )

    code = code.upper()

    # 日本株対応
    if code.isdigit():
        code += ".T"

    img_path = f"{CACHE_DIR}/{code}_{ma_short}_{ma_long}.png"

    # ------------------------
    # キャッシュ利用
    # ------------------------
    if os.path.exists(img_path):
        last_modified = os.path.getmtime(img_path)

        if time.time() - last_modified < CACHE_EXPIRE:
            return templates.TemplateResponse(
                "stock.html",
                {
                    "request": request,
                    "message": f"{code} のチャート（3分で更新）",
                    "img_path": img_path,
                    "ma_short": ma_short,
                    "ma_long": ma_long,
                    "code": code
                }
            )

    # ------------------------
    # 株価取得
    # ------------------------
    data = yf.download(
        code,
        period="3mo",
        progress=False,
        auto_adjust=False,
        threads=False
    )

    if data.empty:
        return templates.TemplateResponse(
            "stock.html",
            {
                "request": request,
                "message": "データが取得できませんでした",
                "img_path": None,
                "ma_short": ma_short,
                "ma_long": ma_long,
                "code": code
            }
        )

    # ------------------------
    # MultiIndex対策
    # ------------------------
    if hasattr(data.columns, "levels"):
        data.columns = data.columns.get_level_values(0)

    required_cols = ["Open", "High", "Low", "Close", "Volume"]

    missing_cols = [
        col for col in required_cols
        if col not in data.columns
    ]

    if missing_cols:
        return templates.TemplateResponse(
            "stock.html",
            {
                "request": request,
                "message": f"必要な列がありません: {missing_cols}",
                "img_path": None,
                "ma_short": ma_short,
                "ma_long": ma_long,
                "code": code
            }
        )

    # ------------------------
    # 欠損値除去
    # ------------------------
    data = data.dropna(subset=required_cols)

    if data.empty:
        return templates.TemplateResponse(
            "stock.html",
            {
                "request": request,
                "message": "有効なデータがありません",
                "img_path": None,
                "ma_short": ma_short,
                "ma_long": ma_long,
                "code": code
            }
        )

    # ------------------------
    # 型変換
    # ------------------------
    for col in ["Open", "High", "Low", "Close"]:
        data[col] = data[col].astype(float)

    data["Volume"] = (
        data["Volume"]
        .fillna(0)
        .astype(int)
    )

    # ------------------------
    # チャート生成
    # ------------------------
    mpf.plot(
        data,
        type="candle",
        mav=(ma_short, ma_long),
        volume=True,
        savefig=img_path
    )

    return templates.TemplateResponse(
        "stock.html",
        {
            "request": request,
            "message": f"{code} のチャートを生成しました",
            "img_path": img_path,
            "ma_short": ma_short,
            "ma_long": ma_long,
            "code": code
        }
    )


