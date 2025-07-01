# src/utils/config_loader.py

import yaml

def load_config(path):
    """
    載入 YAML 設定檔
    參數:
        path (str): 設定檔案路徑
    回傳:
        dict: 解析後的設定內容
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)