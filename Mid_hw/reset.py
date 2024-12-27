from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import SQL

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 忘記密碼頁面
@router.get("/reset", response_class=HTMLResponse)
def reset_password_ui(request: Request):
    return templates.TemplateResponse("/login/reset.html", {"request": request})

# 發送重置郵件
@router.post("/reset", response_class=HTMLResponse)
def send_reset_email(
    request: Request,
    email: str = Form(...),
):
    conn = SQL.get_db()
    cursor = conn.cursor()

    # 檢查郵箱是否存在
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if not user:
        return templates.TemplateResponse(
            "/login/reset.html", {
                "request": request,
                "errors": "該郵箱未註冊"
            }
        )

    # 生成重置令牌和有效期
    reset_token = secrets.token_urlsafe(16)
    reset_expiry = datetime.utcnow() + timedelta(hours=1)

    # 更新數據庫
    cursor.execute(
        "UPDATE users SET reset_token = ?, reset_expiry = ? WHERE email = ?",
        (reset_token, reset_expiry, email)
    )
    conn.commit()
    conn.close()

    reset_link = f"127.0.0.1:8000/reset/{reset_token}"
    send_email(
        recipient=email,
        subject="密碼重置",
        body=f"請點擊以下鏈接重置您的密碼：{reset_link}\n該鏈接一小時內有效。"
    )

    return templates.TemplateResponse(
        "/login/reset.html", {
            "request": request,
            "message": "重置鏈接已發送到您的郵箱"
        }
    )

# 發送郵件函數
def send_email(recipient: str, subject: str, body: str):
    smtp_server = "smtp.gmail.com"  # SMTP 服務地址
    smtp_port = 587  # 常見端口：587 (TLS) 或 465 (SSL)
    sender_email = "s111210513@student.nqu.edu.tw"  # 發件郵箱
    sender_password = "rysf zmwm mgqx ynve"  # 發件郵箱應用程式密碼

    # 創建郵件內容
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # 连接到 SMTP 服务器并发送邮件
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(1)  # 可选：启用调试模式
            server.starttls()  # 启用 TLS 加密
            server.login(sender_email, sender_password)
            server.send_message(message)
    except Exception as e:
        print(f"Failed to send email: {e}")


# 重置密碼頁面
@router.get("/reset/{token}", response_class=HTMLResponse)
def reset_password_form(request: Request, token: str):
    conn = SQL.get_db()
    cursor = conn.cursor()

    # 檢查令牌是否有效
    cursor.execute("SELECT id FROM users WHERE reset_token = ? AND reset_expiry > ?", (token, datetime.utcnow()))
    user = cursor.fetchone()
    if not user:
        return templates.TemplateResponse("/reset/{token}.html", {
            "request": request,
            "error": "鏈接無效或已過期。"
        })

    return templates.TemplateResponse("/login/email_reset.html", {"request": request, "token": token})

# 處理重置密碼請求
@router.post("/reset/{token}")
def reset_password(request: Request, token: str, password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        return templates.TemplateResponse("/login/email_reset.html", {
            "request": request,
            "error": "兩次密碼輸入不一致。",
            "token": token
        })

    conn = SQL.get_db()
    cursor = conn.cursor()

    # 確認令牌是否有效且未過期
    cursor.execute("SELECT id FROM users WHERE reset_token = ? AND reset_expiry > ?", (token, datetime.utcnow()))
    user = cursor.fetchone()
    if not user:
        return templates.TemplateResponse("/login/email_reset.html", {
            "request": request,
            "error": "鏈接無效或已過期。",
            "token": token
        })

    # 檢查新密碼是否與舊密碼不同
    cursor.execute("SELECT id FROM users WHERE id = ? AND password = ?", (user["id"], password))
    existing_password = cursor.fetchone()
    if existing_password:
        return templates.TemplateResponse("/login/email_reset.html", {
            "request": request,
            "error": "新密碼不能與舊密碼相同。",
            "token": token
        })

    # 更新密碼並清空令牌
    cursor.execute(
        "UPDATE users SET password = ?, reset_token = NULL, reset_expiry = NULL WHERE id = ?",
        (password, user["id"])
    )
    conn.commit()
    conn.close()

    return RedirectResponse(url="/login", status_code=302)
