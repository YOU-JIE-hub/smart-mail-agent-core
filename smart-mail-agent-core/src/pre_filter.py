# src/pre_filter.py
import re

# 過濾關鍵字（lowercase 搜尋）
IGNORE_KEYWORDS = [
    r"unsubscribe", r"promotion", r"newsletter", r"廣告",
    r"抽獎", r"優惠券", r"click here", r"bitcoin"
]

# 白名單寄件者（即使符合關鍵字也保留處理）
WHITELIST_SENDERS = {
    "boss@company.com",
    "hr@company.com"
}

def should_process(subject: str, body: str, sender: str) -> bool:
    """
    決定是否應處理該郵件：
    - 若寄件者在白名單 → 一律處理
    - 若主旨與內文皆為空 → 忽略
    - 若包含任何過濾關鍵字 → 忽略
    """
    if sender.lower() in WHITELIST_SENDERS:
        return True
    if not subject.strip() and not body.strip():
        return False
    text = f"{subject} {body}".lower()
    for pat in IGNORE_KEYWORDS:
        if re.search(pat, text, flags=re.I):
            return False
    return True
