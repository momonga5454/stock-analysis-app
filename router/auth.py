from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
import secrets
from dotenv import load_dotenv
from db import get_db

load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="templates")

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

# ------------------------
# CSRFチェック
# ------------------------
def verify_csrf(request: Request, form_token: str):
    cookie_token = request.cookies.get("csrf_token")
    if not cookie_token or cookie_token != form_token:
        raise HTTPException(status_code=403, detail="CSRF token invalid")


# ------------------------
# ユーザー取得
# ------------------------
def get_current_user(request: Request):
    token = request.cookies.get("token")

    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["user_id"])  
    except Exception as e:
        print("JWT ERROR:", e)  # ← デバッグ用
        raise HTTPException(status_code=401, detail="Invalid token")


# ------------------------
# ログイン画面
# ------------------------
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ------------------------
# ログイン処理
# ------------------------
@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    conn=Depends(get_db)
):
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "ユーザーなし"}
        )

    # ✅ bcryptはbytes比較
    if not bcrypt.checkpw(password.encode(), user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "パスワード違い"}
        )

    payload = {
        "user_id": user["id"],
        "exp": datetime.utcnow() + timedelta(hours=12)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    if isinstance(token, bytes):
        token = token.decode("utf-8")


    # ✅ CSRF生成
    csrf_token = secrets.token_hex(16)

    response = RedirectResponse("/", status_code=302)
    response.set_cookie("token", token, httponly=True, path="/")
    response.set_cookie("csrf_token", csrf_token, path="/")

    return response


@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=302)

    # ✅ cookie削除
    response.delete_cookie("token")
    response.delete_cookie("csrf_token")

    return response

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )

@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    conn=Depends(get_db)
):
    if password != password2:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "パスワードが一致しません"}
        )

    cursor = conn.cursor()

    # 既存ユーザー確認
    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )
    if cursor.fetchone():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "ユーザーは既に存在します"}
        )

    # パスワードハッシュ化
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, hashed)
    )

    conn.commit()

    return RedirectResponse("/login", status_code=302)