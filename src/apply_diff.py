# src/apply_diff.py
# 根據 diff 草稿檔（JSON）更新 users.db 中的使用者資料，並記錄修改歷程

import json
import sqlite3
import argparse
from utils.logger import logger

# 資料欄位對應表（將草稿中的「欄位」轉為資料庫欄位）
FIELD_MAP = {
    "phone": "phone",
    "address": "address",
    "name": "name",
    "email": "email"
}

def ensure_diff_log_table(conn):
    """
    建立 diff_log 表格（若尚未存在）
    用於記錄欄位修改歷程
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diff_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            欄位 TEXT,
            原值 TEXT,
            新值 TEXT,
            created_at TEXT
        )
    """)
    conn.commit()

def apply_modifications(draft_path: str, db_path: str):
    """
    根據草稿內容更新 users 資料表，並同步寫入 diff_log

    參數:
        draft_path: 草稿 JSON 檔案路徑
        db_path: SQLite 資料庫路徑
    """
    with open(draft_path, "r", encoding="utf-8") as f:
        draft = json.load(f)

    email = draft.get("email")
    mods = draft.get("修改項目", [])

    if not mods:
        logger.warning(f"草稿中無修改項目，跳過更新：{draft_path}")
        return

    conn = sqlite3.connect(db_path)
    ensure_diff_log_table(conn)
    cursor = conn.cursor()

    success_count = 0
    fail_count = 0

    for item in mods:
        field_key = item.get("欄位")
        new_value = item.get("新值")

        # 檢查草稿內容是否完整
        if not field_key or not new_value:
            logger.warning(f"草稿項目格式不完整，跳過：{item}")
            fail_count += 1
            continue

        field = FIELD_MAP.get(field_key)
        if not field:
            logger.warning(f"未知欄位類型：{field_key}，跳過")
            fail_count += 1
            continue

        try:
            # 實際更新 users 表格中的指定欄位
            logger.info(f"更新 {field} → {new_value}")
            cursor.execute(f"""
                UPDATE users
                SET {field} = ?
                WHERE email = ?
            """, (new_value, email))

            # 同時寫入 diff_log 表記錄此次修改
            cursor.execute("""
                INSERT INTO diff_log (email, 欄位, 原值, 新值, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (email, item.get("欄位"), item.get("原值"), item.get("新值")))

            success_count += 1
        except Exception as e:
            logger.error(f"更新失敗：{field} → {new_value}｜錯誤：{str(e)}")
            fail_count += 1

    conn.commit()
    conn.close()

    logger.info(f"已完成更新：{email}｜成功 {success_count} 項，失敗 {fail_count} 項")

def main():
    """
    主程式：解析 CLI 參數，執行 apply_modifications()
    """
    parser = argparse.ArgumentParser(description="套用 diff 草稿 → 更新使用者資料")
    parser.add_argument("--draft", default="data/output/diff_draft.json", help="草稿檔案路徑")
    parser.add_argument("--db", default="data/users.db", help="資料庫路徑")
    args = parser.parse_args()

    apply_modifications(args.draft, args.db)

if __name__ == "__main__":
    main()
