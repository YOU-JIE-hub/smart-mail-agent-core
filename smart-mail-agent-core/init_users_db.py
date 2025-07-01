# src/init_users_db.py
# 初始化 users.db，並寫入一筆測試使用者資料

import sqlite3
from pathlib import Path

def init_users_db():
    """
    建立 users.db 與 users 資料表，並插入一筆示範資料
    """
    db_path = "data/users.db"
    Path("data").mkdir(exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 建立資料表（若不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            address TEXT
        )
    """)

    # 插入示範使用者
    cursor.execute("""
        INSERT OR REPLACE INTO users (email, name, phone, address)
        VALUES (?, ?, ?, ?)
    """, ("test@example.com", "林小明", "0912345678", "台北市"))

    conn.commit()
    conn.close()
    print("users.db 已建立並寫入測試資料")

if __name__ == "__main__":
    init_users_db()
