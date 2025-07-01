# src/inference_classifier.py
# 使用已訓練的 RoBERTa 分類模型，批量對郵件資料進行推論

import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import argparse
import os

# 預設的標籤順序
LABELS = [
    "請求技術支援",
    "申請修改資訊",
    "詢問流程或規則",
    "投訴與抱怨",
    "業務接洽或報價",
    "其他"
]
id2label = {i: label for i, label in enumerate(LABELS)}

def load_model(model_path):
    """載入 tokenizer 與分類模型"""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    return tokenizer, model

def classify(text, tokenizer, model):
    """對單一郵件文字進行推論，回傳標籤與信心值"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)[0]
        predicted_id = torch.argmax(probs).item()
        return id2label[predicted_id], probs[predicted_id].item()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="outputs/roberta-zh-checkpoint", help="模型資料夾路徑")
    parser.add_argument("--input", required=True, help="輸入 JSON 檔路徑（list 格式）")
    parser.add_argument("--output", help="可選：輸出 JSON 路徑")
    args = parser.parse_args()

    tokenizer, model = load_model(args.model)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)

    results = []
    for item in data:
        text = item.get("subject", "") + item.get("content", "")
        label, score = classify(text, tokenizer, model)
        results.append({
            "subject": item.get("subject", ""),
            "content": item.get("content", ""),
            "predicted_label": label,
            "confidence": round(score, 4)
        })

    for r in results:
        print(f"[{r['predicted_label']}] ({r['confidence']}) - {r['subject']}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"已儲存分類結果到 {args.output}")

if __name__ == "__main__":
    main()