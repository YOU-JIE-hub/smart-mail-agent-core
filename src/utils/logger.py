# src/utils/logger.py
# 建立主 logger，支援輸出至檔案與 console，並減少其他模組訊息

import logging
import warnings
from pathlib import Path

# 建立 logs 資料夾（若不存在）
Path("logs").mkdir(exist_ok=True)

# 日誌輸出檔案路徑
LOG_FILE = "logs/run.log"

# 建立 logger 物件
logger = logging.getLogger("smart-mail-agent")
logger.setLevel(logging.INFO)

# 避免重複新增 handler（例如被多次 import）
if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 檔案輸出 handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Console 輸出 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 加入 handler 至 logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# 降低第三方模組過多的日誌輸出
for noisy in [
    "urllib3",
    "httpx",
    "openai",
    "requests",
    "langchain",
]:
    logging.getLogger(noisy).setLevel(logging.WARNING)

# FAISS 啟動資訊也關閉
logging.getLogger("faiss.loader").setLevel(logging.ERROR)

# 忽略 langchain 中常見警告訊息
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")
