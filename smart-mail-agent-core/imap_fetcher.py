# src/imap_fetcher.py
# 透過 IMAP 自動讀取未讀郵件並呼叫處理 pipeline

import imaplib
import email
from email.header import decode_header
import os
import json
import subprocess
from dotenv import load_dotenv

# 載入環境變數 (.env)
load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("GMAIL_USER")
EMAIL_PASS = os.getenv("GMAIL_PASS")
RECIPIENT = os.getenv("REPLY_TO", EMAIL_USER)  # 回信預設對象

def clean_text(text):
    """清理郵件文字，移除換行與多餘空格"""
    return ''.join(text.splitlines()).strip()

def fetch_unread_emails():
    """取得所有未讀郵件並逐一處理"""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")

    # 搜尋未讀郵件
    status, messages = mail.search(None, '(UNSEEN)')
    email_ids = messages[0].split()
    print(f"共找到 {len(email_ids)} 封未讀信")

    for num in email_ids:
        # 讀取郵件內容
        status, msg_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        subject = msg["Subject"]
        if subject:
            subject, enc = decode_header(subject)[0]
            if isinstance(subject, bytes):
                subject = subject.decode(enc or "utf-8", errors="ignore")

        # 解析郵件內文
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        subject = clean_text(subject)
        body = clean_text(body)

        print(f"處理信件：{subject}")

        # 將郵件內容存為 JSON，提供 pipeline 使用
        input_path = "data/input/from_email.json"
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump({"subject": subject, "body": body}, f, ensure_ascii=False)

        # 呼叫 pipeline 處理這封信件
        subprocess.run([
            "bash", "run_pipeline.sh",
            "--subject", subject,
            "--body", body,
            "--recipient", RECIPIENT,
            "--model", "gpt-3.5-turbo"
        ], check=True)

    mail.logout()

if __name__ == "__main__":
    fetch_unread_emails()
