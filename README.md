# Smart Mail Agent — 智能郵件處理系統

---

## 專案介紹

本系統結合 NLP、RAG、RPA 等技術，自動分類、摘要及智慧處理中文郵件，支援自動回信、報價單產出、投訴道歉信等多項功能。

---

## 專案結構與檔案說明
```
smart-mail-agent-core/
├── .env                      # 環境變數設定檔
├── .gitignore                # Git 忽略設定
├── README.md                 # 專案說明文件（本檔）
├── check_diff_log.py         # 差異紀錄比對輔助工具
├── check_users.py            # 使用者資料查詢輔助工具
├── config
│   └── config.yaml           # 系統主要參數與分類標籤設定
├── dashboard.py              # Streamlit 儀表板，呈現統計圖表與明細
├── data                      # 主要資料庫與輸出目錄
│   ├── emails_log.db         # 郵件處理紀錄 SQLite 資料庫
│   ├── input                 # 輸入資料目錄
│   ├── knowledge             # RAG 知識庫
│   │   ├── faiss_store       # 向量索引檔案（FAISS）
│   │   │   ├── index.faiss
│   │   │   └── index.pkl
│   │   └── faq.md            # FAQ 文字檔
│   ├── output                # 分類結果與回信輸出 JSON
│   │   └── classify_result.json
│   ├── stats.db              # 每日分類統計資料庫
│   ├── train                 # 訓練資料存放（含分類標籤語料）
│   ├── testdata              # 測試郵件資料（可忽略上傳 GitHub）
│   └── users.db              # 使用者資料庫
├── db_init.py                # 資料庫初始化腳本（建立資料表與預設資料）
├── generate_testdata.py      # 自動生成測試郵件 JSON 資料
├── imap_fetcher.py           # IMAP 郵件擷取模組（擴充用）
├── init_users_db.py          # 使用者資料庫初始化輔助腳本
├── log_result.py             # 分類結果寫入 emails_log.db
├── logs
│   └── run.log              # 系統運行日誌
├── observe.sh                # DB 與 Log 快照輔助腳本
├── requirements.txt          # Python 依賴套件列表
├── results                   # 模型權重資料夾（外部下載放置）
│   └── outputs
│       └── roberta-zh-checkpoint/
│           ├── config.json
│           ├── model.safetensors
│           ├── special_tokens_map.json
│           ├── tokenizer.json
│           ├── tokenizer_config.json
│           └── vocab.txt
├── run_all_tests.sh          # 一鍵批次測試腳本
├── snapshot_after.txt        # 觀察檔案與資料庫快照
├── snapshot_before.txt       # 觀察檔案與資料庫快照
└── src                       # 系統核心模組
    ├── action_handler.py     # 分類後續動作路由觸發主程式
    ├── apply_diff.py         # 更新使用者資料庫模組
    ├── classifier.py         # 中文意圖分類模型推論
    ├── classify.py           # CLI 介面分類腳本
    ├── draft_review.py       # 比對資料異動草稿產生
    ├── handle_complaint.py   # 投訴郵件道歉信處理
    ├── inference_classifier.py # 分類推論測試腳本
    ├── main.py               # 主流程入口（分類+動作）
    ├── pre_filter.py         # 郵件預處理與過濾
    ├── quote_generator.py    # 報價單 PDF 產生模組
    ├── quote_selector.py     # 報價方案選擇器
    ├── rag_answer_generator.py # RAG 問答生成
    ├── reply_email.py        # 郵件回信功能（含 HTML、附件）
    ├── send_with_attachment.py # 帶附件郵件寄送模組
    ├── stats_collector.py    # 統計資料更新與管理
    ├── summarizer.py         # 中文郵件摘要生成
    ├── support_ticket.py     # 技術支援工單建立
    ├── train_classifier.py   # 分類模型訓練腳本
    └── utils
        ├── alert.py          # Slack 警報及錯誤重試裝飾器
        ├── config_loader.py  # 設定檔讀取工具
        ├── db_tools.py       # 資料庫查詢與更新輔助
        ├── label_action_map.py # 分類標籤與動作對應
        └── logger.py         # 日誌設定與工具
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
