# src/log_result.py
"""
把「未自動處理」郵件記進 emails_log.db
"""
import argparse, sqlite3, datetime, pathlib, logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DB = pathlib.Path("data") / "emails_log.db"

def log_email(subject, label, confidence, summary=""):
    ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    with sqlite3.connect(DB) as conn:
        conn.execute("""INSERT INTO emails_log
            (subject, category, summary, action, error, timestamp)
            VALUES (?,?,?,?,?,?)""",
            (subject, label, summary, "logged", f"conf={confidence:.3f}", ts))
    logging.info("已寫入 emails_log：%s | %s", label, subject[:40])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--confidence", type=float, required=True)
    args = ap.parse_args()
    log_email(args.subject, args.label, args.confidence)
