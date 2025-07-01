import os
import sqlite3
import json
import logging
import shutil

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# 紀錄執行過程中的錯誤訊息
errors = []

# 1. 建立 data 資料夾與測試資料目錄
try:
    os.makedirs('data', exist_ok=True)
    if os.path.exists('data/testdata'):
        shutil.rmtree('data/testdata')  # 刪除舊的測試資料目錄（若存在）
    os.makedirs('data/testdata')
    logging.info("Created 'data/testdata' directory for test files.")
except Exception as e:
    logging.error("Failed to create test data directory: %s", e)
    errors.append(f"Directory creation error: {e}")

# 2. 初始化 SQLite 資料庫 (users.db)
try:
    if os.path.exists('data/users.db'):
        os.remove('data/users.db')  # 重新建立前先移除舊檔
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id   INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            role TEXT
        )
    """)
    # 插入示範使用者資料
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email, role) VALUES (1, 'Alice', 'alice@example.com', 'customer')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email, role) VALUES (2, 'Bob', 'bob@example.com', 'support_agent')")
    conn.commit()
    conn.close()
    logging.info("Initialized 'data/users.db' with table 'users' (2 demo users inserted).")
except Exception as e:
    logging.error("Failed to initialize users.db: %s", e)
    errors.append(f"Database users.db error: {e}")

# 3. 初始化 SQLite 資料庫 (emails_log.db)
try:
    if os.path.exists('data/emails_log.db'):
        os.remove('data/emails_log.db')
    conn = sqlite3.connect('data/emails_log.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails_log (
            id        INTEGER PRIMARY KEY,
            subject   TEXT,
            category  TEXT,
            summary   TEXT,
            action    TEXT,
            error     TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()
    logging.info("Initialized 'data/emails_log.db' with table 'emails_log' (empty log ready).")
except Exception as e:
    logging.error("Failed to initialize emails_log.db: %s", e)
    errors.append(f"Database emails_log.db error: {e}")

# 4. 準備分類模型測試郵件資料列表
test_emails = []

# 類別: 技術支援 (Technical Support)
test_emails.append({
    "filename": "tech_support_01.json",
    "subject": "無法登入帳號問題",
    "body": "您好，我無法登入我的帳號，系統顯示密碼錯誤，但我確定密碼是正確的。請協助解決這個問題，謝謝！",
    "expected_category": "技術支援",
    "expected_summary": "用戶無法登入帳號，請求技術支援協助處理。"
})
test_emails.append({
    "filename": "tech_support_02.json",
    "subject": "登入錯誤與截圖",
    "body": "您好：\n我在使用貴服務時遇到錯誤。系統一直出現未知錯誤訊息，詳情請見附件截圖。\n謝謝。",
    "expected_category": "技術支援",
    "expected_summary": "用戶遇到系統錯誤（有提及附件），尋求技術支援。",
    "attachments": ["error_screenshot.png"]  # 模擬附件遺失: 提供附件檔名但實際不附檔
})

# 類別: 申請修改資訊 (Information Update Request)
test_emails.append({
    "filename": "info_update_01.json",
    "subject": "請求更新聯絡電話",
    "body": "您好，\n我最近更換了手機號碼，想請貴公司更新我帳戶上的聯絡電話。\n原號碼: 0912345678\n新號碼: 0987654321\n謝謝您的協助。",
    "expected_category": "申請修改資訊",
    "expected_summary": "客戶請求更新帳戶聯絡電話資訊。"
})
test_emails.append({
    "filename": "info_update_02.json",
    "subject": "更正帳戶地址資訊",
    "body": "To whom it may concern,\n我在帳戶上的郵寄地址有誤，想請求協助更正。\n目前地址：台北市中正區XX路1號\n正確地址：台北市中山區YY路99號\n謝謝。",
    "expected_category": "申請修改資訊",
    "expected_summary": "客戶要求更正帳戶的郵寄地址資訊。"
})

# 類別: 業務接洽 (Business Contact)
test_emails.append({
    "filename": "business_contact_01.json",
    "subject": "詢問合作與服務報價",
    "body": "您好，\n我們是ABC公司，對貴公司的產品很感興趣，想進一步了解企業合作方案和服務報價。如有相關資訊，請提供給我們，謝謝！\nBest Regards,\nABC Co.",
    "expected_category": "業務接洽",
    "expected_summary": "企業客戶詢問合作方案及服務報價。"
})
test_emails.append({
    "filename": "business_contact_02.json",
    "subject": "洽談商業合作機會",
    "body": "Hi,\n我們想與貴公司討論潛在的商業合作機會。我們有一項新計畫，希望能尋求合作可能。如果您有興趣，請回覆我們安排會議時間。謝謝！\nXYZ Corp.",
    "expected_category": "業務接洽",
    "expected_summary": "潛在合作夥伴詢問商業合作的可能性，希望安排會議討論。"
})

# 類別: 投訴 (Complaint)
test_emails.append({
    "filename": "complaint_01.json",
    "subject": "對最近服務的不滿",
    "body": "Dear Customer Service,\n我對最近使用貴服務的體驗感到非常失望。預訂過程中出現多次錯誤，客服回覆也非常慢。我希望能得到合理的解釋和補償。\n謝謝，\n一位不滿的用戶",
    "expected_category": "投訴",
    "expected_summary": "用戶對服務體驗不滿，抱怨預訂問題和客服反應慢，要求解釋和補償。"
})
test_emails.append({
    "filename": "complaint_02.json",
    "subject": "投訴：帳單收費錯誤",
    "body": "您好：\n我的信用卡帳單顯示貴公司重複收費。我對此非常不滿，請立即調查並退還多收的款項。\n謝謝。\n客戶 張三",
    "expected_category": "投訴",
    "expected_summary": "客戶發現帳單重複收費，提出投訴要求退款。"
})

# 類別: 詢問規則 (Rules Inquiry)
test_emails.append({
    "filename": "rules_inquiry_01.json",
    "subject": "詢問取消預訂的規則",
    "body": "請問如果我現在預訂飯店後想取消，相關的取消規定是什麼？是否可以全額退款？謝謝！",
    "expected_category": "詢問規則",
    "expected_summary": "客戶詢問預訂取消的規定和退款政策。"
})
test_emails.append({
    "filename": "rules_inquiry_02.json",
    "subject": "關於使用禮券的規則",
    "body": "Hello,\n我想了解一下你們網站上使用禮券的相關規則。如果我有一張100美元的禮券，可以分多次使用嗎？還是只能一次用完？謝謝！",
    "expected_category": "詢問規則",
    "expected_summary": "客戶詢問網站禮券使用規則，可否分次使用一張禮券。"
})

# 類別: 其他 (Others)
test_emails.append({
    "filename": "others_01.json",
    "subject": "",
    "body": "",
    "expected_category": "其他",
    "expected_summary": "郵件無內容，無法判斷分類。"
})
test_emails.append({
    "filename": "others_02.json",
    "subject": "Test",
    "body": "asdf1234 ?? ??",
    "expected_category": "其他",
    "expected_summary": "郵件內容無法識別，歸入其他類別。"
})

# 5. 將測試郵件資料寫入 JSON 檔案
for email in test_emails:
    try:
        filename = email["filename"]
        # 準備內容（移除 filename 欄位，不寫入 JSON）
        content = {k: v for k, v in email.items() if k != "filename"}
        filepath = os.path.join("data/testdata", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        logging.info(f"Created test email file: {filename}")
    except Exception as e:
        logging.error("Failed to write test file %s: %s", email.get("filename", "?"), e)
        errors.append(f"File write error ({email.get('filename')}): {e}")

# 6. 產生說明 README 檔案
try:
    readme_path = os.path.join("data/testdata", "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# 測試資料一覽\n\n")
        for email in test_emails:
            fname = email["filename"]
            cat = email["expected_category"]
            subj = email["subject"] if email["subject"] else "（無主旨）"
            summ = email["expected_summary"]
            # 標註特殊觸發行為的郵件
            note = ""
            if fname == "tech_support_01.json":
                note = "（此郵件預期觸發自動建立工單）"
            elif fname == "info_update_01.json":
                note = "（此郵件預期觸發自動產生比對草稿）"
            elif fname == "business_contact_01.json":
                note = "（此郵件預期觸發自動產生 PDF 報價單）"
            line = f"- **{fname}**：類別「{cat}」，主旨「{subj}」，預期摘要：「{summ}」{note}\n"
            f.write(line)
    logging.info("Created 'data/testdata/README.md' with descriptions of test emails.")
except Exception as e:
    logging.error("Failed to write README.md for test data: %s", e)
    errors.append(f"README write error: {e}")

# 結束訊息
if errors:
    logging.error("Test data generation completed with errors. Please check the above logs.")
else:
    logging.info("Test data generation completed successfully.")
