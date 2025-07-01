#!/usr/bin/env bash
set -euo pipefail

PHASE=${1:-run}                       # before / after / run
OUT="snapshot_${PHASE}.txt"           # 輸出檔

{
echo "====== $(date '+%F %T')  [$PHASE] ======"

# 目錄
echo -e "\n# folder tree"
find . -maxdepth 2 -type f | sort

# 最新 40 行 log
echo -e "\n# tail logs/run.log"
[ -f logs/run.log ] && tail -n 40 logs/run.log || echo "(no log yet)"

# users.db
echo -e "\n# users.db (全部)"
sqlite3 -column -header data/users.db "SELECT * FROM users;"

# emails_log.db：統計 + 最新 10 筆
echo -e "\n# emails_log.db counts"
sqlite3 -column -header data/emails_log.db "SELECT category,COUNT(*) as cnt FROM emails_log GROUP BY category;"
echo -e "\n# emails_log.db last 10"
sqlite3 -column -header data/emails_log.db "SELECT id,subject,category,timestamp FROM emails_log ORDER BY id DESC LIMIT 10;"

# stats.db：今日各分類計數
echo -e "\n# stats.db today"
sqlite3 -column -header data/stats.db "SELECT label,count FROM daily_stats WHERE dt=date('now','localtime');"

echo "=============== end [$PHASE] =================="
} | tee "$OUT"
chmod 644 "$OUT"
echo "存到 $OUT"
