# src/utils/label_action_map.py
# 回傳每個標籤（label）實際在本系統中對應的動作行為說明（與 action_handler.py 一致）

def get_action_for_label(label: str) -> str:
    """
    根據分類標籤，回傳對應的處理動作說明（用於介面顯示或日誌記錄）

    標籤來源對應 action_handler.py
    """
    action_map = {
        "請求技術支援": "建立工單並記錄摘要內容",
        "詢問流程或規則": "使用 RAG 回覆內容並寄出郵件",
        "申請修改資訊": "產出草稿差異檔並更新 users.db",
        "投訴與抱怨": "寄送道歉信並發出警示通知",
        "業務接洽或報價": "選擇報價方案並寄送 PDF 附件（或手動通知）",
        "其他": "寫入 log_result 並記錄信心值"
    }
    return action_map.get(label, "無定義處理流程")
