# generate_env_example.py

import os

env_example = """
# ========================
#  OpenAI API 設定
# ========================
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ========================
#  Gmail SMTP 設定
# ========================
GMAIL_USER=your_email@gmail.com
GMAIL_PASS=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465

# ========================
#  IMAP 設定（若啟用收信）
# ========================
IMAP_SERVER=imap.gmail.com

# ========================
#  測試收件者信箱（回信會寄到這）
# ========================
REPLY_TO=your_email@gmail.com

# ========================
#  Slack 警報通知 Webhook
# ========================
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz

# ========================
#  錯誤通知 Email（擴充用）
# ========================
ALERT_EMAIL_TO=devops@example.com
""".strip()

with open(".env.example", "w", encoding="utf-8") as f:
    f.write(env_example + "\n")

print("✅ 已成功產生 .env.example")
