# src/support_ticket.py

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from utils.logger import logger

DB_PATH = "data/tickets.db"

def init_db():
    """
    初始化支援工單資料表
    """
    Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            content TEXT,
            summary TEXT,
            created_at TEXT,
            status TEXT,
            priority TEXT
        )
    """)
    conn.commit()
    conn.close()

def decide_priority(text):
    """
    根據主旨與內容判斷優先等級（若有關鍵字則為高優先）
    """
    high_keywords = [
        "無法登入", "錯誤", "系統當掉", "系統異常", "客戶反應", "全部無法使用",
        "全公司", "所有人", "系統掛掉", "停擺", "無法操作"
    ]
    for word in high_keywords:
        if word in text:
            return "high"
    return "normal"

def create_ticket(subject, content, summary):
    """
    建立一筆技術支援工單
    """
    init_db()
    priority = decide_priority(subject + content)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.utcnow().isoformat()

    cursor.execute("""
        INSERT INTO support_tickets (subject, content, summary, created_at, status, priority)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (subject, content, summary, created_at, "pending", priority))

    conn.commit()
    conn.close()
    logger.info(f"已建立技術支援工單：{subject}（{priority}）")

def main():
    parser = argparse.ArgumentParser(description="建立技術支援工單")
    parser.add_argument("--subject", type=str, required=True, help="信件主旨")
    parser.add_argument("--content", type=str, required=True, help="信件內容")
    parser.add_argument("--summary", type=str, default="", help="信件摘要")
    args = parser.parse_args()

    create_ticket(args.subject, args.content, args.summary)

if __name__ == "__main__":
    main()
