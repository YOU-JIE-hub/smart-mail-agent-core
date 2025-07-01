# src/check_users.py
# 簡易列出 users.db 內所有使用者資料

import sqlite3
from pathlib import Path

DB_PATH = Path("data/users.db")

def query_users():
    """
    連線至 users.db 並列印所有使用者資料
    """
    if not DB_PATH.exists():
        print(f"找不到資料庫：{DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print(row)

if __name__ == "__main__":
    query_users()
