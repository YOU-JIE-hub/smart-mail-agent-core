# src/reply_email.py

import smtplib
import argparse
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

# 設定日誌格式
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 載入 .env 中的 Gmail 帳密與 SMTP 設定
load_dotenv()
SENDER_EMAIL   = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASS")
SMTP_SERVER    = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT      = int(os.getenv("SMTP_PORT", 465))


def send_email(
    sender: str,
    password: str,
    recipient: str,
    subject: str,
    body: str,
    smtp_server: str,
    port: int,
    is_html: bool = False
):
    """
    發送 Email：支援 HTML 與純文字格式，使用 SMTP_SSL 驗證
    """
    try:
        if is_html:
            # 使用 HTML 格式
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = recipient
            part = MIMEText(body, "html", "utf-8")
            msg.attach(part)
        else:
            # 使用純文字格式
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = recipient

        # 透過 Gmail SMTP 發信
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())

        logging.info("郵件已成功寄出")

    except smtplib.SMTPAuthenticationError:
        logging.error("驗證失敗：請確認帳密正確，或是否啟用 Gmail 應用程式密碼")
        exit(1)
    except Exception as e:
        logging.error(f"發送失敗：{e}")
        exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True, help="輸入 JSON 檔（需包含 query 和 answer）")
    parser.add_argument("--recipient", required=True, help="收件者 email")
    parser.add_argument("--mode", choices=["send", "dryrun"], default="dryrun")
    parser.add_argument("--html", action="store_true", help="是否以 HTML 格式寄出")
    args = parser.parse_args()

    try:
        with open(args.json, "r", encoding="utf-8") as f:
            data = json.load(f)

        subject = f"RE: {data['query']}"
        body    = data["answer"]

        if args.mode == "dryrun":
            print("預覽信件：")
            print("Subject:", subject)
            print("To:", args.recipient)
            print("HTML:", args.html)
            print("Body:")
            print(body)
        else:
            send_email(
                sender=SENDER_EMAIL,
                password=GMAIL_PASSWORD,
                recipient=args.recipient,
                subject=subject,
                body=body,
                smtp_server=SMTP_SERVER,
                port=SMTP_PORT,
                is_html=args.html
            )

    except FileNotFoundError:
        logging.error(f"找不到輸入檔案：{args.json}")
    except KeyError as e:
        logging.error(f"JSON 檔缺少必要欄位：{e}")
    except Exception as e:
        logging.error(f"發生錯誤：{e}")


if __name__ == "__main__":
    main()
