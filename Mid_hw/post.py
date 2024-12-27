from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import File, UploadFile
import os  
from login import get_current_user
from markdown import markdown
import SQL
import time
from typing import List
import json

templates = Jinja2Templates(directory="templates")

router = APIRouter()

# 新增文章頁面
@router.get("/post/new", response_class=HTMLResponse)
def new_post_ui(request: Request):
    user = get_current_user(request)  # 確認用戶是否登入
    if not user:
        return RedirectResponse(url="/?error=請先登錄")  # 傳遞錯誤信息給登錄頁面
    return templates.TemplateResponse("/post/new_post.html", {"request": request})  # 渲染新文章頁面

# 創建新文章
@router.post("/post")
async def create_post(
    request: Request,   
    title: str = Form(...), # 從表單中獲取文章標題
    body: str = Form(...),  # 從表單中獲取文章內容
    images: List[str] = Form([])  # 接收圖片URL列表
):
    user = get_current_user(request) # 確認用戶是否登入
    if not user:
        return RedirectResponse(url="/?error=請先登錄") # 傳遞錯誤信息給登錄頁面

    conn = SQL.get_db()
    cursor = conn.cursor()
    
    try:
        # 開始事務
        cursor.execute("BEGIN TRANSACTION")
        
        # 插入文章，包含 images 字段
        cursor.execute(
            "INSERT INTO posts (username, title, body, images) VALUES (?, ?, ?, ?)",
            (user["username"], title, body, json.dumps(images))
        )
        post_id = cursor.lastrowid
        
        # 記錄圖片到 post_images 表
        for image_url in images:
            if image_url.startswith("/static/uploads/"):
                image_path = image_url.replace("/static/uploads/", "")
                cursor.execute(
                    "INSERT INTO post_images (post_id, image_path) VALUES (?, ?)",
                    (post_id, image_path)
                )
        
        # 提交事務
        cursor.execute("COMMIT")
        conn.close()
        return RedirectResponse(url="/", status_code=302)
    
    except Exception as e:
        # 發生錯誤時回滾事務
        cursor.execute("ROLLBACK")
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# 查看用戶自己的貼文
@router.get("/post/my-posts", response_class=HTMLResponse)
def view_my_posts(request: Request):
    user = get_current_user(request) 
    if not user:
        return RedirectResponse(url="/?error=請先登錄")

    conn = SQL.get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, title, body FROM posts WHERE username = ?",
        (user["username"],),
    )  # 查詢當前用戶的貼文
    posts = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "/post/my_posts.html",
        {"request": request, "posts": posts, "user": user},
    )

# 查看單篇文章
@router.get("/post/{post_id}", response_class=HTMLResponse)
def view_post(request: Request, post_id: int):
    user = get_current_user(request)
    conn = SQL.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, title, body FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    conn.close()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    content_html = markdown(post["body"])
    return templates.TemplateResponse(
        "/post/show_post.html",
        {"request": request, "post": post, "content_html": content_html, "user": user},
    )

#上傳圖片
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload/image")
async def upload_image(request: Request, file: UploadFile = File(...)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=403, detail="請先登錄")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只允許上傳圖片文件")

    # 生成唯一的文件名（避免文件名衝突）
    filename = f"{user['username']}_{int(time.time())}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {"url": f"/static/uploads/{filename}"}

# 刪除貼文
@router.delete("/post/{post_id}")
def delete_post(request: Request, post_id: int):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=403, detail="請先登錄")

    conn = SQL.get_db()
    cursor = conn.cursor()
    
    try:
        # 開始事務
        cursor.execute("BEGIN TRANSACTION")
        
        # 檢查權限
        cursor.execute("SELECT username FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        
        if not post or post["username"] != user["username"]:
            raise HTTPException(status_code=403, detail="無權刪除此貼文")
        
        # 獲取創建時間戳記範圍
        cursor.execute("SELECT created_at FROM posts WHERE id = ?", (post_id,))
        created_at = cursor.fetchone()["created_at"]
        
        # 刪除文章
        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        
        # 提交數據庫更改
        cursor.execute("COMMIT")
        
        # 刪除對應時間範圍內的用戶圖片
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith(f"{user['username']}_"):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    # 可以進一步檢查文件創建時間
                    os.remove(file_path)
                    print(f"圖片文件已刪除: {file_path}")
                except Exception as e:
                    print(f"刪除圖片文件失敗: {e}")
        
        return {"message": "貼文已刪除"}
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

# 修改貼文頁面
@router.get("/post/edit/{post_id}", response_class=HTMLResponse)
def edit_post_ui(request: Request, post_id: int):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/?error=請先登錄")
    
    conn = SQL.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, title, body FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    conn.close()

    if not post or post["username"] != user["username"]:
        raise HTTPException(status_code=403, detail="無權訪問此頁面")

    return templates.TemplateResponse(
        "/post/edit_post.html",
        {"request": request, "post": post}
    )

# 更新貼文
@router.post("/post/edit/{post_id}")
def update_post(
    request: Request,
    post_id: int,
    title: str = Form(...),
    body: str = Form(...)
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/?error=請先登錄")

    conn = SQL.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()

    if not post or post["username"] != user["username"]:
        raise HTTPException(status_code=403, detail="無權修改此貼文")

    post = cursor.fetchone()
    cursor.execute("UPDATE posts SET title = ?, body = ? WHERE id = ?", (title, body, post_id))
    conn.commit()
    conn.close()

    return RedirectResponse(url=f"/post/{post_id}", status_code=302)

# 在路由器部分添加新的搜尋功能
@router.get("/search")
def search_posts(request: Request, query: str = "", search_type: str = "all"):
    user = get_current_user(request)
    conn = SQL.get_db()
    cursor = conn.cursor()
    
    search_query = f"%{query}%"
    
    if search_type == "title":
        cursor.execute("""
            SELECT id, username, title, body 
            FROM posts 
            WHERE title LIKE ?
            ORDER BY created_at DESC
        """, (search_query,))
    elif search_type == "content":
        cursor.execute("""
            SELECT id, username, title, body 
            FROM posts 
            WHERE body LIKE ?
            ORDER BY created_at DESC
        """, (search_query,))
    elif search_type == "author":
        cursor.execute("""
            SELECT id, username, title, body 
            FROM posts 
            WHERE username LIKE ?
            ORDER BY created_at DESC
        """, (search_query,))
    else:  # search_type == "all"
        cursor.execute("""
            SELECT id, username, title, body 
            FROM posts 
            WHERE title LIKE ? 
            OR body LIKE ? 
            OR username LIKE ?
            ORDER BY created_at DESC
        """, (search_query, search_query, search_query))
    
    posts = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse(
        "/post/list.html",
        {
            "request": request,
            "user": user,
            "posts": posts,
            "query": query,
            "search_type": search_type
        }
    )