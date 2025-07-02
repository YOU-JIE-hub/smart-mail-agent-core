#!/usr/bin/env python
# src/action_handler.py
# 根據分類結果 label，觸發對應自動處理模組；最後把耗時寫進 stats.db

import argparse, json, subprocess, tempfile, os, time, importlib
from utils.logger import logger
from stats_collector import increment_counter
import log_result as lr

def route_action(label: str, data: dict) -> None:
    """根據 predicted_label 觸發相應動作"""
    subject = data.get("subject", "")
    body    = data.get("body", "")
    summary = data.get("summary", "")
    sender  = data.get("sender") or data.get("email") or data.get("recipient")

    start = time.time()

    if label == "請求技術支援":
        logger.info("分類為『請求技術支援』，建立工單")
        subprocess.run(
            ["python", "src/support_ticket.py",
             "--subject", subject, "--content", body, "--summary", summary],
            check=True)

    # 詢問規則 → RAG 回覆
    elif label == "詢問流程或規則":
        logger.info("分類為『詢問流程或規則』，啟動 RAG 回覆")
        subprocess.run(
            ["python", "src/rag_answer_generator.py",
             "--query", body, "--label", label,
             "--kb", "data/knowledge/faq.md",
             "--output", "data/output/reply_gpt35.json"],
            check=True)
        logger.info("RAG 完成，寄出回信")
        subprocess.run(
            ["python", "src/reply_email.py",
             "--json", "data/output/reply_gpt35.json",
             "--mode", "send", "--recipient", sender, "--html"],
            check=True)

    elif label == "申請修改資訊":
        logger.info("分類為『申請修改資訊』，產出 diff 並更新資料庫")
        subprocess.run(
            ["python", "src/draft_review.py",
             "--email", sender, "--subject", subject, "--content", body,
             "--output", "data/output/diff_draft.json"],
            check=True)
        subprocess.run(
            ["python", "src/apply_diff.py",
             "--draft", "data/output/diff_draft.json", "--db", "data/users.db"],
            check=True)

    elif label == "投訴與抱怨":
        logger.info("分類為『投訴與抱怨』，啟動道歉回信流程")
        from handle_complaint import handle_complaint_action
        handle_complaint_action(data)

    elif label == "業務接洽或報價":
        logger.info("分類為『業務接洽或報價』，產生報價單 / 或手動確認")
        from quote_selector import choose_package
        sel = choose_package(subject, body)

        if sel["needs_manual"]:
            from send_with_attachment import send_email_with_attachment
            ack = "<p>您好，已收到您的需求，專人將盡速與您聯繫。</p>"
            send_email_with_attachment(
                recipient=sender,
                subject=f"RE: {subject} - 已收到需求",
                body_html=ack,
                attachment_path=None,
            )
        else:
            from quote_generator import generate_quote_pdf_pretty
            pdf_path = os.path.join(tempfile.gettempdir(), "quote.pdf")
            generate_quote_pdf_pretty(
                output_path=pdf_path,
                client_name=sender,
                package_name=sel["package"],
            )
            from send_with_attachment import send_email_with_attachment
            html_body = (
                f"<p>您好，附件為 <b>{sel['package']}</b> 報價單，"
                "若有疑問歡迎回覆。</p>"
            )
            send_email_with_attachment(
                recipient=sender,
                subject=f"RE: {subject} - 報價單",
                body_html=html_body,
                attachment_path=pdf_path,
            )

    else:
        logger.info("分類為『%s』，僅記錄 log", label)
        lr.log_email(subject, label, data.get("confidence", 0))

    elapsed = round(time.time() - start, 3)
    increment_counter(label, elapsed)
    logger.info("統計完成：%s (+1)，耗時 %.3fs", label, elapsed)

def main() -> None:
    ap = argparse.ArgumentParser(description="根據分類結果觸發動作")
    ap.add_argument("--json", required=True, help="分類結果 JSON 檔")
    args = ap.parse_args()

    with open(args.json, encoding="utf-8") as f:
        data = json.load(f)

    label = data.get("predicted_label", "其他")
    logger.info("讀取分類結果：%s → %s", args.json, label)
    route_action(label, data)
# ──────────────────────────────────────────
if __name__ == "__main__":
    main()
