import sqlite3

# 設定 SQLite3 資料庫連線
def get_db():
    conn = sqlite3.connect("blog.db")  # 連接SQLite3資料庫
    conn.row_factory = sqlite3.Row  # 使查詢結果以字典形式返回，便於根據列名訪問
    return conn  # 返回資料庫連線對象

def init_db():
    conn = get_db()  # 獲取資料庫連線
    cursor = conn.cursor()  # 創建一個游標對象，用於執行SQL查詢
    
    # 創建用戶表格
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            reset_token TEXT,
            reset_expiry DATETIME
        );
    """)
    
    # 創建文章表格
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            images TEXT DEFAULT '[]',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 創建文章圖片表格
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
        );
    """)
    
    conn.commit()  # 提交改動
    conn.close()  # 關閉資料庫連線

def update_db_schema():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 尝试查询 reset_token 列，如果不存在会抛出异常
        cursor.execute("SELECT reset_token FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # 如果列不存在，添加新列
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    
    try:
        # 尝试查询 reset_expiry 列，如果不存在会抛出异常
        cursor.execute("SELECT reset_expiry FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # 如果列不存在，添加新列
        cursor.execute("ALTER TABLE users ADD COLUMN reset_expiry DATETIME")
    
    try:
        # 尝试查询 created_at 列，如果不存在会抛出异常
        cursor.execute("SELECT created_at FROM posts LIMIT 1")
    except sqlite3.OperationalError:
        # 如果列不存在，添加新列
        cursor.execute("ALTER TABLE posts ADD COLUMN created_at DATETIME")
    
    try:
        # 尝试查询 updated_at 列，如果不存在会抛出异常
        cursor.execute("SELECT updated_at FROM posts LIMIT 1")
    except sqlite3.OperationalError:
        # 如果列不存在，添加新列
        cursor.execute("ALTER TABLE posts ADD COLUMN updated_at DATETIME")
    
    conn.commit()
    conn.close()

def upgrade_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Create post_images table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        );
    """)
    
    try:
        # Check if post_images table exists
        cursor.execute("SELECT * FROM post_images LIMIT 1")
    except sqlite3.OperationalError:
        # Create post_images table
        cursor.execute("""
            CREATE TABLE post_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            );
        """)
    
    conn.commit()
    conn.close()
