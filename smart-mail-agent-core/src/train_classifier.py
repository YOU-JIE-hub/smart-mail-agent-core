# src/train_classifier.py

import os
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

MODEL_NAME = "hfl/chinese-roberta-wwm-ext"
DATA_PATH = "data/train/emails_classified.json"
OUTPUT_DIR = "outputs/roberta-zh-checkpoint"
LABELS = [
    "請求技術支援",
    "申請修改資訊",
    "詢問流程或規則",
    "投訴與抱怨",
    "業務接洽或報價",
    "其他"
]

label2id = {label: i for i, label in enumerate(LABELS)}
id2label = {i: label for label, i in label2id.items()}

# 讀取 JSON 格式資料
dataset = load_dataset("json", data_files=DATA_PATH, split="train")

# 將文字標籤轉為數字索引
def preprocess_labels(example):
    example["label"] = label2id[example["label"]]
    return example

dataset = dataset.map(preprocess_labels)

# 切分訓練/驗證集
dataset = dataset.train_test_split(test_size=0.2, seed=42)
train_dataset = dataset["train"]
eval_dataset = dataset["test"]

# 載入 tokenizer 與模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(LABELS)
)

# 編碼輸入內容
def tokenize_function(examples):
    return tokenizer(examples["content"], truncation=True, padding=True, max_length=512)

train_dataset = train_dataset.map(tokenize_function, batched=True)
eval_dataset = eval_dataset.map(tokenize_function, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# 訓練參數設定
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    eval_strategy="epoch",
    save_strategy="epoch",
    num_train_epochs=5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    logging_dir="./logs",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
)

# 評估指標
def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    labels = p.label_ids
    acc = accuracy_score(labels, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted")
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}

# 啟動 Trainer 訓練
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

trainer.train()
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print("模型訓練完成並儲存至", OUTPUT_DIR)
