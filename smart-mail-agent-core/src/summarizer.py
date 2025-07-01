# src/summarizer.py

from transformers import pipeline

def summarize_email(text, config):
    """
    使用指定模型對郵件內容進行摘要

    參數：
        text (str): 郵件原始內容
        config (dict): 設定檔，需包含 summary.model 欄位

    回傳：
        str: 摘要文字
    """
    model_name = config["summary"]["model"]
    summarizer_pipe = pipeline("summarization", model=model_name)

    summary = summarizer_pipe(
        text,
        max_length=100,
        min_length=20,
        do_sample=False,
        truncation=True
    )

    return summary[0]["summary_text"]
