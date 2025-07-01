# src/check_diff_log.py
# 檢視最近 10 筆使用者資料異動紀錄（diff_log）

import sqlite3
from tabulate import tabulate
from pathlib import Path

DB_PATH = Path("data/users.db")

def check_diff_log():
    """
    讀取 diff_log 表格並顯示最近 10 筆異動紀錄
    """
    if not DB_PATH.exists():
        print(f"找不到資料庫：{DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, 欄位, 原值, 新值, created_at
        FROM diff_log
        ORDER BY created_at DESC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()

    print(
        tabulate(
            rows,
            headers=["Email", "欄位", "原值", "新值", "時間"],
            tablefmt="grid"
        )
    )

if __name__ == "__main__":
    check_diff_log()
