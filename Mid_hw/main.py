from fastapi import FastAPI, Request, Form, Depends, HTTPException  # FastAPI核心模組
from fastapi.responses import HTMLResponse, RedirectResponse  # HTML與重定向響應模組
from fastapi.templating import Jinja2Templates  # 用於渲染HTML模板
from fastapi.staticfiles import StaticFiles  # 提供靜態資源服務
from itsdangerous import URLSafeSerializer  # 用於加密與解密Session資料
import uvicorn  # 用於啟動開發伺服器
import SQL  

from login import router as login_router,get_current_user
from reset import router as reset_router
from post import router as post_router

# ------------------ FastAPI ------------------
app = FastAPI()  # 創建FastAPI應用

# 使用itsdangerous進行Session管理
SECRET_KEY = "your_secret_key"  # 設定加密密鑰
serializer = URLSafeSerializer(SECRET_KEY)  # 創建序列化器實例

# 設定模板和靜態檔案目錄
templates = Jinja2Templates(directory="templates")  # 指定模板目錄
app.mount("/static", StaticFiles(directory="static"), name="static")  # 指定靜態文件目錄

# ------------------ 資料庫操作 ------------------
SQL.init_db()  # 初始化資料庫
SQL.upgrade_db()  # 更新資料庫
SQL.update_db_schema()  # 更新資料庫架構
# ------------------ 首頁 ------------------
@app.get("/", response_class=HTMLResponse)
def list_posts(request: Request):
    user = get_current_user(request)  # 獲取當前用戶資料
    conn = SQL.get_db()  # 資料庫連接
    cursor = conn.cursor()  # 游標物件
    title = "歡迎來到 test post"
    cursor.execute("SELECT id, username, title, body FROM posts")  # 查詢所有文章
    posts = cursor.fetchall()  # 獲取文章列表
    conn.close()  # 關閉資料庫
    return templates.TemplateResponse(
        "/post/list.html",
        {"request": request, "user": user, "posts": posts, "title": title},
    )  # 渲染模板，傳遞數據

# ------------------ 路由處理 ------------------
app.include_router(post_router)
app.include_router(login_router) 
app.include_router(reset_router)

# ------------------ 主執行程式 ------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)  # 啟動伺服器
