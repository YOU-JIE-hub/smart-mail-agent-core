# Smart Mail Agent — 智能郵件處理系統

---

## 專案介紹

本系統結合 NLP、RAG、RPA 等技術，自動分類、摘要及智慧處理中文郵件，支援自動回信、報價單產出、投訴道歉信等多項功能。
適合 AI / RPA 工程師求職展示，提供完整實務能力證明。

---

## 專案結構與檔案說明

```
smart-mail-agent-core/
├── .env.example             # 環境變數範例（請依此建立 .env）
├── README.md                # 專案說明文件（本檔）
├── requirements.txt         # Python 相依套件列表
├── scripts/
│   ├── db_init.py           # 資料庫初始化腳本
│   ├── generate_testdata.py # 自動產生測試郵件資料
│   ├── run_all_tests.sh     # 一鍵批次測試腳本
│   └── download_model.sh    # （示範）模型下載腳本（本案使用 Google Drive 另行下載）
├── data/
│   ├── users.db             # 使用者資料庫
│   ├── emails_log.db        # 郵件處理記錄
│   ├── stats.db             # 分類統計資料
│   ├── knowledge/faq.md     # FAQ 知識庫文件（RAG 使用）
│   ├── output/              # 分類與回信結果輸出
│   └── testdata/            # 測試郵件 JSON（6 類共 12 封）
├── results/                 # 模型權重資料夾（需自行下載放入）
│   └── roberta-zh-checkpoint/
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       ├── tokenizer_config.json
│       ├── special_tokens_map.json
│       └── vocab.txt
├── src/
│   ├── main.py              # 主流程入口（分類+後續動作）
│   ├── action_handler.py    # 根據分類路由動作觸發
│   ├── classifier.py        # 分類模型推論
│   ├── summarizer.py        # 中文摘要模組
│   ├── rag_answer_generator.py # RAG 問答回覆模組
│   ├── reply_email.py       # 回信寄送（HTML 支援）
│   ├── send_with_attachment.py # 附件郵件寄送
│   ├── handle_complaint.py  # 投訴回信處理
│   ├── quote_generator.py   # PDF 報價單產生
│   ├── support_ticket.py    # 技術支援工單建立
│   ├── utils/               # 工具函式（DB、Logger、Alert 等）
│   └── ...                  # 其他輔助模組
```

---

## 模型權重下載說明

由於模型權重檔案較大，**未包含於 GitHub 專案內**。

請前往以下 Google Drive 下載完整模型資料夾：

[https://drive.google.com/drive/folders/1M4-A1uaNFcfHG72tLBvwaGYVZ0s9F2jH?usp=sharing](https://drive.google.com/drive/folders/1M4-A1uaNFcfHG72tLBvwaGYVZ0s9F2jH?usp=sharing)

下載後，請將整個 `results` 資料夾放置於專案根目錄下，確保目錄結構如下：

```
smart-mail-agent-core/
├── results/
│   └── roberta-zh-checkpoint/
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       ├── tokenizer_config.json
│       ├── special_tokens_map.json
│       └── vocab.txt
```

---

## 環境變數 `.env` 設定說明

請依照 `.env.example` 建立專屬於你的 `.env` 檔案，放置於專案根目錄（切勿上傳 GitHub）。

```dotenv
# OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Gmail SMTP 設定
GMAIL_USER=your_email@gmail.com
GMAIL_PASS=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465

# IMAP 設定（可選，若啟用收信功能）
IMAP_SERVER=imap.gmail.com

# 回信預設收件者（測試用）
REPLY_TO=your_email@gmail.com

# Slack 警報 Webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz

# 錯誤通知 Email（擴充用）
ALERT_EMAIL_TO=devops@example.com
```

---

## 安裝流程

```bash
python3 -m venv .venv1
source .venv1/bin/activate
pip install -r requirements.txt
```

---

## 初始化資料庫

```bash
PYTHONPATH=src python scripts/db_init.py --reset
```

---

## 產生測試資料

```bash
python scripts/generate_testdata.py
```

---

## 一鍵測試

```bash
bash scripts/run_all_tests.sh
```

---

## CLI 使用範例

```bash
PYTHONPATH=src python src/main.py \
  --subject "詢問合作與服務報價" \
  --body "您好，我們是ABC公司，想了解貴公司報價方案" \
  --sender your_email@gmail.com
```
