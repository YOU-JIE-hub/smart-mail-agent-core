# src/stats_collector.py

import sqlite3, datetime, os
from utils.logger import logger

DB_PATH = "data/stats.db"
os.makedirs("data", exist_ok=True)

def _today() -> str:
    """回傳今日日期（格式：YYYY-MM-DD）"""
    return datetime.date.today().isoformat()

def _conn():
    """建立資料庫連線並初始化 daily_stats 資料表"""
    c = sqlite3.connect(DB_PATH)
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            dt TEXT,
            label TEXT,
            count INTEGER DEFAULT 0,
            total_sec REAL DEFAULT 0,
            PRIMARY KEY (dt, label)
        )
    """)
    return c

def increment_counter(label: str, delta_sec: float = 0.0):
    """
    更新指定 label 的統計資訊：
    - 每次呼叫將 count +1
    - 累加處理所耗時間（可為 0）
    """
    conn = _conn()
    conn.execute("""
        INSERT INTO daily_stats(dt, label, count, total_sec)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(dt, label) DO UPDATE
        SET count = count + 1,
            total_sec = total_sec + excluded.total_sec
    """, (_today(), label, delta_sec))
    conn.commit()
    conn.close()

    logger.debug(f"已更新統計資訊：{label}")
