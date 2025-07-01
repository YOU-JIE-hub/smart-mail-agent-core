# src/main.py
import argparse
import subprocess
import sys
import os
import json

from utils.logger import logger
from pre_filter import should_process

CLASSIFY_OUT = "data/output/classify_result.json"
os.makedirs("data/output", exist_ok=True)

def run_classification(subject: str, body: str) -> None:
    """呼叫分類模組，產出分類結果 JSON"""
    logger.info("開始執行信件分類")
    env = os.environ.copy()
    env["PYTHONPATH"] = env.get("PYTHONPATH", "") + ":."
    subprocess.run(
        [
            "python",
            "-m", "src.classify",
            "--subject", subject,
            "--body", body,
            "--output", CLASSIFY_OUT
        ],
        check=True,
        env=env,
    )

def inject_sender(sender: str) -> None:
    """將寄件者寫入分類結果 JSON，供後續模組使用"""
    with open(CLASSIFY_OUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["sender"] = sender
    with open(CLASSIFY_OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def run_action_handler() -> None:
    """根據分類結果觸發對應後續處理"""
    logger.info("根據分類結果觸發後續處理")
    subprocess.run(
        ["python", "src/action_handler.py", "--json", CLASSIFY_OUT],
        check=True,
    )

def main() -> None:
    parser = argparse.ArgumentParser(description="郵件分類與自動處理主控流程")
    parser.add_argument("--subject", required=True, help="郵件主旨")
    parser.add_argument("--body", required=True, help="郵件內文")
    parser.add_argument("--sender", required=True, help="寄件者 E-mail")
    args = parser.parse_args()

    # 1. 執行前置過濾
    if not should_process(args.subject, args.body, args.sender):
        logger.info("前置過濾：忽略該郵件")
        sys.exit(0)

    # 2. 分類郵件
    run_classification(args.subject, args.body)

    # 3. 將寄件者寫入分類結果
    inject_sender(args.sender)

    # 4. 根據分類結果執行後續處理模組
    run_action_handler()

    logger.info("自動化流程完成")

if __name__ == "__main__":
    main()
