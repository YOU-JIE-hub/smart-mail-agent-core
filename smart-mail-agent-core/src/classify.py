# src/classify.py
# 獨立分類工具：從 CLI 接收主旨與內文，呼叫分類模型進行意圖預測，並儲存 JSON 結果

import argparse
import json
import os
from .classifier import classify_email

def main() -> None:
    """
    主程式：解析 CLI 參數，執行分類，將結果輸出成 JSON 檔
    """
    parser = argparse.ArgumentParser(description="分類輸入的信件主旨與內文")
    parser.add_argument("--subject", type=str, required=True, help="郵件主旨")
    parser.add_argument("--body",    type=str, required=True, help="郵件內文")
    parser.add_argument(
        "--output",
        type=str,
        default="data/output/classify_result.json",
        help="輸出 JSON 路徑"
    )
    args = parser.parse_args()

    # 呼叫主分類函式
    result = classify_email(args.subject, args.body)

    # 確保輸出資料夾存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # 輸出結果至 JSON 檔案
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("分類完成，結果已儲存至", args.output)

if __name__ == "__main__":
    main()