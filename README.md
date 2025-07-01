# Smart Mail Agent — 智能郵件處理系統

---

## 專案介紹

本專案旨在打造一套 AI 自動郵件處理平台，整合 NLP、LLM、RPA 技術，透過信件分類、摘要、知識檢索與自動後續動作（如寄送報價單、建立工單、更新資料庫），支援以下任務：
1. 自動讀取郵件內容（主旨＋內文）
2. 中文語意分類（意圖判別）
3. 關鍵句摘要（文字簡化）
4. 根據分類觸發後續自動處理（寄信、產出草稿、記錄等）
5. 支援 CLI 操作與 Linux 排程部署
6. 所有動作均有記錄至資料庫，並提供視覺化查詢方式（Dashboard）

特色:
1. 使用自訓練 RoBERTa 中文分類模型
2. 加入 RAG 結合 LangChain 提供智慧回覆
3. 自動產出 PDF 報價單、資料異動草稿、客服道歉信等對應動作
4. 全流程自動記錄 log、分類結果、處理時間、動作歷程
5. 完整資料庫整合與 SQLite 快速部署

### 分類標籤定義與處理對應關係

```markdown
| 分類標籤         | 意圖說明                           | 自動化處理行為                                                |
|------------------|------------------------------------|---------------------------------------------------------------|
| 請求技術支援     | 使用者遇到系統錯誤、無法登入、功能異常等問題       | 自動建立客服工單紀錄，留存處理狀態與聯絡資訊                            |
| 申請修改資訊     | 請求變更帳號資訊，如聯絡電話、地址、姓名等         | 比對內文與現有資料，產出變更草稿（diff 結構），供後續審核與執行               |
| 詢問流程或規則   | 詢問退款條件、使用限制、服務時間、訂單處理等相關問題 | 將問題送入內建 FAQ 知識庫，透過 RAG（檢索式問答）生成自動回覆                      |
| 投訴與抱怨       | 表達不滿、負面體驗、服務不周等客訴內容               | 自動生成並寄送道歉與後續聯繫說明之回信                                |
| 業務接洽或報價   | 商業合作、詢問服務方案、需求報價等正式商務聯繫       | 自動產出報價單（PDF 附檔），並附回信回覆                                 |
| 其他             | 非明確意圖、無法分類或無需處理之信件內容             | 僅記錄至 log 與資料庫，不主動觸發任何後續動作                            |
```



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
        ├── alert.py          # Slack
        ├── config_loader.py  # 設定檔讀取工具
        ├── db_tools.py       # 資料庫查詢
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
PYTHONPATH=src python src/inference_classifier.py \
  --model outputs/roberta-zh-checkpoint \
  --subject "我要修改聯絡資料" \
  --content "您好，我的手機號碼更新為 0911111111，請幫我更新帳戶資料。" \
  --output data/output/classify_result.json
```
請先確認你已完成分類模型訓練，模型儲存於：outputs/roberta-zh-checkpoint/
