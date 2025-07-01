# src/utils/db_tools.py

import sqlite3
from typing import Dict, Optional

def get_user_by_email(db_path: str, email: str) -> Optional[Dict]:
    """
    根據 email 查詢單一使用者資料

    參數:
        db_path (str): SQLite 資料庫檔案路徑
        email (str): 要查詢的使用者 email

    回傳:
        dict 或 None: 若有找到回傳 dict，否則回傳 None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, name, phone, address
        FROM users
        WHERE email = ?
    """, (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "email": row[1],
            "name": row[2],
            "phone": row[3],
            "address": row[4]
        }
    else:
        return None

def get_all_users(db_path: str) -> list:
    """
    查詢所有使用者資料（全部欄位）

    參數:
        db_path (str): SQLite 資料庫檔案路徑

    回傳:
        list[dict]: 所有使用者資料清單
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name, phone, address FROM users")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "email": row[1],
            "name": row[2],
            "phone": row[3],
            "address": row[4]
        }
        for row in rows
    ]

# 單元測試區塊：可直接執行本模組進行測試查詢
if __name__ == "__main__":
    db_path = "data/users.db"

    print("使用 get_all_users() 查詢所有使用者：")
    for user in get_all_users(db_path):
        print(user)

    print("\n使用 get_user_by_email() 查詢 test@example.com：")
    user = get_user_by_email(db_path, "test@example.com")
    print(user)