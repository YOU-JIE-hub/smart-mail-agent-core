# src/send_with_attachment.py

import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
from utils.logger import logger
from utils.alert import retry_with_alert

# 載入 Gmail SMTP 憑證與參數
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT   = int(os.getenv("SMTP_PORT", 465))
SENDER      = os.getenv("GMAIL_USER")
PASSWORD    = os.getenv("GMAIL_PASS")


@retry_with_alert(max_retry=3)
def send_email_with_attachment(recipient: str, subject: str,
                               body_html: str, attachment_path: str | None):
    """
    寄送帶有附件的 HTML 格式郵件
    - 若無附件，可傳入 attachment_path=None
    - 自動套用 GMAIL_USER / GMAIL_PASS 作為寄件者
    """

    # 驗證環境變數是否載入
    if not (SENDER and PASSWORD):
        raise ValueError("GMAIL_USER / GMAIL_PASS 未設定")

    # 組裝結構
    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = SENDER, recipient, subject
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    # 若有附件，加入 MIMEApplication
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part["Content-Disposition"] = (
            f'attachment; filename="{os.path.basename(attachment_path)}"'
        )
        msg.attach(part)

    # 使用 SMTP 寄送郵件
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
        s.login(SENDER, PASSWORD)
        s.sendmail(SENDER, recipient, msg.as_string())

    logger.info(f"已寄出郵件至 {recipient}（是否包含附件：{bool(attachment_path)})")
