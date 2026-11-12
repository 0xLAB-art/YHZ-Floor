#!/usr/bin/env bash
# finish the kimi cohorts' transport-only pairs (paced APINEX, serial)
set -u
cd "$(dirname "$0")"
LOG="KIMI_FINISH_20261103.log"
say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }
for c in info_contract_label5_20261030__rerun_ar_20261103 info_contract_label5r_20261030__rerun_ar_20261103; do
  say "resume $c (serial, paced adapter)"
  python3 -u shard_base_main.py "$c" 1 >> "$LOG" 2>&1 && say "done $c" || say "FAIL $c"
done
say "kimi finish complete"
