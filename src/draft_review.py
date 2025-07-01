# src/draft_review.py
# 根據使用者信件內容與現有資料，擷取欲修改欄位並產出草稿 JSON 檔（供審核與後續 apply 使用）

import re
import json
import argparse
from datetime import datetime
from utils.db_tools import get_user_by_email
from utils.logger import logger

# 欄位變更的容錯型表示式：可接受多種語句格式
PATTERNS = [
    (r"(?:電話|聯絡電話)[是為從由 ]+(\d+)[\s]*(?:改為|變更為|換成)[\s]*(\d+)", "phone"),
    (r"(?:地址)[是為從由 ]+(\S+)[\s]*(?:改為|變更為|換成)[\s]*(\S+)", "address"),
    (r"(?:姓名|名稱)[是為從由 ]+(\S+)[\s]*(?:改為|變更為|換成)[\s]*(\S+)", "name"),
    (r"(?:email|信箱)[是為從由 ]+(\S+)[\s]*(?:改為|變更為|換成)[\s]*(\S+)", "email")
]

def extract_modifications(text: str, user_data: dict) -> list:
    """
    擷取信件中與使用者資料不一致的欄位修改需求

    回傳格式：
    [
        {"欄位": "phone", "原值": "0912345678", "新值": "0987654321"},
        ...
    ]
    """
    results = []
    for pattern, field in PATTERNS:
        match = re.search(pattern, text)
        if match and user_data:
            old_value, new_value = match.groups()
            new_value = new_value.strip().rstrip("。.,，、 ")
            if user_data.get(field) == old_value:
                results.append({
                    "欄位": field,
                    "原值": old_value,
                    "新值": new_value
                })
    return results

def generate_diff_draft(email: str, subject: str, content: str, output_path: str):
    """
    根據寄件者 email 查詢資料庫，並解析信件內容是否有欄位變更需求
    若有則產生 diff 草稿 JSON 檔
    """
    user_data = get_user_by_email("data/users.db", email=email)
    if not user_data:
        logger.warning(f"查無 email 使用者：{email}，無法產生草稿")
        return

    modifications = extract_modifications(content, user_data)

    draft = {
        "email": email,
        "修改項目": modifications,
        "建立時間": datetime.utcnow().isoformat(),
        "狀態": "草稿",
        "主旨": subject
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)

    logger.info(f"草稿已輸出至 {output_path}")

def main():
    """
    CLI 主程式：接收 email、主旨與內容，產生差異草稿
    """
    parser = argparse.ArgumentParser(description="申請修改資訊 → 擷取 diff 草稿")
    parser.add_argument("--email", required=True, help="寄件者 email（用來查舊資料）")
    parser.add_argument("--subject", required=True, help="信件主旨")
    parser.add_argument("--content", required=True, help="信件內容")
    parser.add_argument("--output", default="data/output/diff_draft.json", help="輸出草稿路徑")
    args = parser.parse_args()

    generate_diff_draft(args.email, args.subject, args.content, args.output)

if __name__ == "__main__":
    main()
