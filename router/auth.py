from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
import secrets
import os
from dotenv import load_dotenv

# ================================
#  初期設定
# ================================
load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# JWT 設定
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 12


# ================================
#  CSRF トークン検証
# ================================
def verify_csrf(request: Request, form_token: str):
    cookie_token = request.cookies.get("csrf_token")
    if not cookie_token or cookie_token != form_token:
        raise HTTPException(status_code=403, detail="CSRF token invalid")


# ================================
#  JWT からユーザー名を取り出す
# ================================
def get_current_user(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=302, headers={"Location": "/login"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]  # username
    except:
        raise HTTPException(status_code=302, headers={"Location": "/login"})


# ================================
#  ログインページ（GET）
# ================================
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


# ================================
#  ログイン処理（POST）
# ================================
@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect("stocks.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    # bcrypt で照合
    if not row or not bcrypt.checkpw(password.encode(), row[0]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "ユーザー名またはパスワードが違います"}
        )

    # JWT を作成
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # CSRF トークン生成
    csrf_token = secrets.token_hex(32)

    # Cookie に JWT と CSRF を保存
    response = RedirectResponse("/", status_code=302)

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=True,        # ← HTTPS 前提
        samesite="lax",
        path="/"
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,     # ← hidden フィールドで使うため
        secure=True,
        samesite="lax",
        path="/"
    )

    return response


# ================================
#  ログアウト
# ================================
@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie("token")
    response.delete_cookie("csrf_token")
    return response


# ================================
#  新規登録ページ（GET）
# ================================
@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


# ================================
#  新規登録処理（POST）
# ================================
@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    csrf_token: str = Form(...)
):
    # CSRF チェック
    verify_csrf(request, csrf_token)

    # パスワード一致チェック
    if password != password2:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "パスワードが一致しません"}
        )

    # bcrypt でハッシュ化
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = sqlite3.connect("stocks.db")
    cursor = conn.cursor()

    # すでに存在するユーザー名か確認
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone()

    if exists:
        conn.close()
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "このユーザー名はすでに使われています"}
        )

    # 新規ユーザー登録
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, hashed)
    )
    conn.commit()
    conn.close()

    # 登録後はログインページへ
    return RedirectResponse("/login", status_code=302)

