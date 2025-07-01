# src/utils/alert.py

import os, time, smtplib, requests
from email.mime.text import MIMEText
from functools import wraps
from utils.logger import logger

# 讀取環境變數（Slack、Email、SMTP 設定）
SLACK_WEBHOOK  = os.getenv("SLACK_WEBHOOK_URL", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
GMAIL_USER     = os.getenv("GMAIL_USER")
GMAIL_PASS     = os.getenv("GMAIL_PASS")
SMTP_SERVER    = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT      = int(os.getenv("SMTP_PORT", 465))

# 發送 Slack 
def send_slack(message: str):
    if not SLACK_WEBHOOK:
        return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=5)
    except Exception as e:
        logger.error(f"Slack 告警失敗：{e}")

# 發送 Email 
def send_email_alert(message: str):
    if not (ALERT_EMAIL_TO and GMAIL_USER and GMAIL_PASS):
        return
    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = "Smart-Mail-Agent 告警"
    msg["From"]    = GMAIL_USER
    msg["To"]      = ALERT_EMAIL_TO
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
            s.login(GMAIL_USER, GMAIL_PASS)
            s.sendmail(GMAIL_USER, ALERT_EMAIL_TO, msg.as_string())
    except Exception as e:
        logger.error(f"E-mail 告警失敗：{e}")

# 若連續失敗，發送 Slack 與 Email 
def retry_with_alert(max_retry=3, delay=5):
    """
    retry_with_alert 裝飾器：
    - 當被包裝的函式執行失敗時會自動重試（最多 max_retry 次）
    - 若連續失敗則會發送 Slack 與 Email 告警
    """
    def deco(func):
        @wraps(func)
        def wrap(*args, **kw):
            for i in range(1, max_retry + 1):
                try:
                    return func(*args, **kw)
                except Exception as e:
                    logger.error(f"{func.__name__} 第 {i} 次失敗：{e}")
                    time.sleep(delay)
            # 連續失敗
            msg = f"{func.__name__} 連續 {max_retry} 次失敗！"
            logger.error(msg)
            send_slack(msg)
            send_email_alert(msg)
            raise
        return wrap
    return deco