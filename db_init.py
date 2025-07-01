# scripts/db_init.py
# 建立或修補所有 SQLite 資料表：users.db、emails_log.db、stats.db

import argparse, sqlite3, pathlib, os, logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DATA = pathlib.Path("data")
DATA.mkdir(exist_ok=True)

def ensure(conn: sqlite3.Connection, ddl: str):
    conn.execute(ddl)
    conn.commit()

def add_column(conn, table: str, col: str, ddl_type: str):
    cur = conn.execute(f"PRAGMA table_info({table})")
    if col not in [row[1] for row in cur.fetchall()]:
        logging.info("ALTER %s ADD COLUMN %s", table, col)
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl_type}")
        conn.commit()

def init_users(reset=False):
    db = DATA / "users.db"
    if reset and db.exists():
        db.unlink()
    with sqlite3.connect(db) as conn:
        ensure(conn, """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            address TEXT,
            role TEXT
        )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO users
            (id, name, email, phone, address, role)
            VALUES
            (1, 'Alice', 'alice@example.com', '0912345678', '台北市信義區', 'customer'),
            (2, 'Bob',   'bob@example.com',   '0987654321', '新北市板橋區', 'support_agent')
        """)

def init_emails_log(reset=False):
    db = DATA / "emails_log.db"
    if reset and db.exists():
        db.unlink()
    with sqlite3.connect(db) as conn:
        ensure(conn, """
        CREATE TABLE IF NOT EXISTS emails_log (
            id INTEGER PRIMARY KEY,
            subject TEXT,
            category TEXT,
            summary TEXT,
            action TEXT,
            error TEXT,
            timestamp TEXT
        )
        """)

def init_stats(reset=False):
    db = DATA / "stats.db"
    if reset and db.exists():
        db.unlink()
    with sqlite3.connect(db) as conn:
        ensure(conn, """
        CREATE TABLE IF NOT EXISTS daily_stats (
            dt TEXT,
            label TEXT,
            count INTEGER DEFAULT 0,
            total_sec REAL DEFAULT 0,
            PRIMARY KEY (dt, label)
        )
        """)
        # 若舊表缺欄位，自動補上
        add_column(conn, "daily_stats", "total_sec", "REAL DEFAULT 0")
        add_column(conn, "daily_stats", "dt", "TEXT")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="Drop and recreate all DBs")
    args = ap.parse_args()

    init_users(args.reset)
    init_emails_log(args.reset)
    init_stats(args.reset)
    logging.info("Database init / schema check complete.")
