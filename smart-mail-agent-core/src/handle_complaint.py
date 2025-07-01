# src/handle_complaint.py

import os
from dotenv import load_dotenv
from datetime import datetime
from send_with_attachment import send_email_with_attachment
from utils.db_tools import get_user_by_email

load_dotenv()

def handle_complaint_action(data: dict):
    email = data.get("sender") or data.get("email")
    subject = data.get("subject", "")
    body    = data.get("body", "")

    # 查詢使用者名稱
    user = get_user_by_email("data/users.db", email)
    name = user.get("name") if user else "貴賓"

    html = f"""
    <p>{name}您好：</p>
    <p>我們已收到您的寶貴意見，對於此次造成的不便，我們深感抱歉。</p>
    <p>我們將轉交專人儘速處理，並努力避免類似情況再次發生。</p>
    <p>若有任何補充需求，歡迎直接回覆此信。</p>
    <p>客服團隊 敬上<br>{datetime.now().strftime('%Y-%m-%d')}</p>
    """

    send_email_with_attachment(
        recipient=email,
        subject=f"RE: {subject} - 很抱歉造成您的困擾",
        body_html=html,
        attachment_path=None,
    )
