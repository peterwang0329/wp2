from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, ValidationError
from itsdangerous import URLSafeSerializer
from typing import Optional
import SQL  

# 創建路由器
router = APIRouter()

# 模板設置
templates = Jinja2Templates(directory="templates")

# 使用 itsdangerous 進行 Session 管理
SECRET_KEY = "your_secret_key"
serializer = URLSafeSerializer(SECRET_KEY)

# ------------------ Session管理 ------------------
# 獲取當前用戶
def get_current_user(request: Request) -> Optional[dict]:
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    try:
        return serializer.loads(session_token)
    except Exception:
        return None

# 設置 Session
def set_session(response, user_data):
    session_token = serializer.dumps(user_data)
    response.set_cookie(key="session_token", value=session_token)

# 清除 Session
def clear_session(response):
    response.delete_cookie(key="session_token")

#----------------------------------------------------------------

# 路由：註冊頁面
@router.get("/signup", response_class=HTMLResponse)
def signup_ui(request: Request):
    return templates.TemplateResponse("/login/signup.html", {"request": request, "title": "註冊"})

# 路由：處理註冊
@router.post("/signup", response_class=HTMLResponse)
def signup(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    errors_sign = {}
    if not username.strip():
        errors_sign["username"] = "用户名不能為空"
    if not password.strip():
        errors_sign["password"] = "密碼不能為空"
    if not email.strip():
        errors_sign["email"] = "電子郵箱不能為空"

    # 檢查郵箱格式
    try:
        class EmailValidationModel(BaseModel):
            email: EmailStr
        EmailValidationModel(email=email)
    except ValidationError:
        errors_sign["email"] = "请输入有效的邮箱地址"

    conn = SQL.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        errors_sign["username"] = "该用户名已存在"

    if errors_sign:
        return templates.TemplateResponse(
            "/login/signup.html", {"request": request, "errors": errors_sign, "username": username, "email": email, "title": "註冊"}
        )

    cursor.execute(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        (username.strip(), password.strip(), email.strip()),
    )
    conn.commit()
    conn.close()

    return RedirectResponse(url="/login", status_code=302)

# 路由：登入頁面
@router.get("/login", response_class=HTMLResponse)
def login_ui(request: Request):
    return templates.TemplateResponse("/login/login.html", {"request": request, "errors": {}, "username": "", "title": "登入"})

# 路由：處理登入
@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    error_login = ""
    if not username.strip() or not password.strip():
        error_login = "用户名和密碼不能為空"
    else:
        conn = SQL.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if not user:
            error_login = "用戶名或密碼錯誤"

    if error_login:
        return templates.TemplateResponse(
            "/login/login.html", {"request": request, "errors": error_login, "username": username, "title": "登入"}
        )

    response = RedirectResponse(url="/", status_code=302)
    set_session(response, {"id": user["id"], "username": user["username"]})
    return response

# 路由：登出
@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/", status_code=302)
    clear_session(response)
    return response
