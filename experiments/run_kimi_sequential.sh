#!/usr/bin/env bash
# kimi-k3 cohorts on APINEX are hard-limited to 15 requests/min: run them
# strictly sequentially, each with the paced adapter (1 shard).
set -u
cd "$(dirname "$0")"
LOG="KIMI_SEQUENTIAL_20261103.log"
say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }
for c in info_contract_label5_20261030 info_contract_label5r_20261030; do
  say "start $c (serial, paced)"
  python3 -u rerun_ar_clone.py "$c" --shards 1 >> "$LOG" 2>&1 \
    && say "done $c" || say "FAIL $c"
done
say "kimi sequential complete"
