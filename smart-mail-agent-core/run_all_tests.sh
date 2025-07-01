#!/usr/bin/env bash
# 批次測試：跑 12 封 JSON 並比對分類結果

set -e
source .venv1/bin/activate

fail=0
for f in data/testdata/*.json; do
  [[ "$f" == *README.md ]] && continue

  subj=$(jq -r '.subject' "$f")
  body=$(jq -r '.body' "$f")
  expect=$(jq -r '.expected_category' "$f")

  # 執行分類 + 處理流程
  PYTHONPATH=. python src/main.py \
    --subject "$subj" \
    --body "$body" \
    --sender "h125872359@gmail.com"

  # 擷取預測標籤
  got=$(jq -r '.predicted_label' data/output/classify_result.json)

  if [[ "$got" != "$expect" ]]; then
    echo "[FAIL] $f => predicted: $got / expected: $expect"
    fail=$((fail+1))
  else
    echo "[ OK ] $f => $got"
  fi
done

echo "==========================="
[[ $fail -eq 0 ]] && echo "[ALL PASS]" || echo "[FAILED: $fail case(s)]"
