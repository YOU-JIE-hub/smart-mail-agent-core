#!/usr/bin/env python
# src/classifier.py
"""
意圖分類主模組：
  1. 使用 fine-tuned RoBERTa 模型預測標籤
  2. 若信心值低或符合特定關鍵字 / 負面語氣，將套用 fallback label 強制改類別
"""

import re
import json
import os
from pathlib import Path
from typing import Dict
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# 載入 fine-tuned 分類模型
MODEL_PATH = "outputs/roberta-zh-checkpoint"
tokenizer  = AutoTokenizer.from_pretrained(MODEL_PATH)
model      = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
clf        = pipeline("text-classification", model=model, tokenizer=tokenizer)

# fallback 關鍵詞與正規表達式（報價 / 負面情緒）
RE_QUOTE  = re.compile(r"(報價|quotation|price)", re.I)
NEG_WORDS = ["爛", "糟", "無法", "抱怨", "氣死", "差"]
NEG_RE    = re.compile("|".join(map(re.escape, NEG_WORDS)))

def sentiment_is_negative(text: str) -> bool:
    """簡易情緒偵測：出現負面詞則判定為負面"""
    return bool(NEG_RE.search(text))

def classify_email(subject: str, body: str) -> Dict[str, str | float]:
    """
    主函式：結合主旨與內文，回傳分類結果與信心值
    自動 fallback 至「投訴」或「業務」以降低誤判

    回傳：
        dict: {
            predicted_label: str,
            confidence: float,
            subject: str,
            body: str
        }
    """
    text = subject + " " + body

    # 模型預測
    pred = clf(text, truncation=True)[0]  # e.g. {'label': 'faq', 'score': 0.92}
    label_map = {
        "support": "請求技術支援",
        "faq": "詢問流程或規則",
        "modify": "申請修改資訊",
        "complaint": "投訴與抱怨",
        "quote": "業務接洽或報價",
        "other": "其他",
    }
    model_label = label_map.get(pred["label"].lower(), "其他")
    confidence  = float(pred["score"])

    # fallback 規則覆寫
    fallback_label = model_label
    if RE_QUOTE.search(text):
        fallback_label = "業務接洽或報價"
    elif sentiment_is_negative(text):
        fallback_label = "投訴與抱怨"

    # 若信心值低或 fallback 判斷與模型不一致，使用 fallback label
    if confidence < 0.55 or fallback_label != model_label:
        final_label = fallback_label
    else:
        final_label = model_label

    return {
        "predicted_label": final_label,
        "confidence": confidence,
        "subject": subject,
        "body": body,
    }

# CLI 測試用法：
# python src/classifier.py --subject "我要改地址" --body "住址改為台北市..." --output data/output/classify_result.json
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    result = classify_email(args.subject, args.body)
    os.makedirs(Path(args.output).parent, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("分類完成，結果已儲存至", args.output)
