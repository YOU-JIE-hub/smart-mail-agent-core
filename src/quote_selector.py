#!/usr/bin/env python
"""
quote_selector.py
根據郵件內容決定報價處理方式：
    • package_name: 自動判斷的方案名稱（用於產出 PDF）
    • needs_manual: 是否需人工判斷（True 表示不產出報價單，僅發確認信）
"""

import re
from typing import Dict

# 關鍵字判斷用正則：是否需客製
KW_ONPREM  = re.compile(r"on[- ]?prem|客製|custom", re.I)
# 關鍵字判斷：是否提及 RPA 相關需求
KW_RPA     = re.compile(r"\b(rpa|自動化)\b", re.I)

def choose_package(subject: str, body: str) -> Dict[str, str | bool]:
    """
    根據信件主旨與內容，決定適合的方案與是否需要人工處理
    回傳格式：
        {
            "package": "方案名稱" 或 None,
            "needs_manual": True/False
        }
    """
    text = f"{subject} {body}"

    # 1. 若提及客製 / on-prem，強制轉人工
    if KW_ONPREM.search(text):
        return {"package": None, "needs_manual": True}

    # 2. 若提及 RPA，自動選定 RPA 方案
    if KW_RPA.search(text):
        return {"package": "RPA 標準方案", "needs_manual": False}

    # 3. 預設回傳 AI 入門方案
    return {"package": "AI 顧問入門方案", "needs_manual": False}


# CLI 測試模式（方便單獨呼叫驗證）
if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("--subject", required=True)
    p.add_argument("--body",    required=True)
    args = p.parse_args()

    result = choose_package(args.subject, args.body)
    print(json.dumps(result, ensure_ascii=False, indent=2))
