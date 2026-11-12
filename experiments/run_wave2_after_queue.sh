#!/usr/bin/env bash
# Wave-2 chained runner: waits for the 14-cohort rerun queue to finish, then
# (1) A3b transport recovery for the A3 pass's 18 HTTP_ERROR pairs,
# (2) P026 C2 floor-sensitivity cohort (96 sessions, floor 8000).
# Everything logged to WAVE2_20261103.log. Restart-safe: skips completed parts.
set -u
cd "$(dirname "$0")"
LOG="WAVE2_20261103.log"
say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }

say "wave2 watcher armed; waiting for rerun_ar_queue.sh to finish"
while pgrep -f "[r]erun_ar_queue.sh" >/dev/null; do sleep 120; done
say "queue finished; starting A3b transport recovery"

if [ -f info_contract_aesgcm_random_p021ar_20261103/amendment_a3b/summary.json ]; then
  say "skip A3b (already complete)"
else
  ( cd info_contract_aesgcm_random_p021ar_20261103 && \
    python3 -u run_p021ar_a3b_topup.py ) >> "$LOG" 2>&1 \
    && say "A3b done" || say "A3b FAILED (see amendment_a3b logs)"
fi

say "starting P026 C2 floor-sensitivity (96 sessions, floor 8000)"
if [ -f info_contract_aesgcm_c2_floor8000_p026_20261103/summary.json ]; then
  say "skip P026 (already complete)"
else
  ( cd info_contract_aesgcm_c2_floor8000_p026_20261103 && \
    python3 -u run_p026_c2_floor8000.py ) >> "$LOG" 2>&1 \
    && say "P026 done" || say "P026 FAILED (see its runner logs)"
fi

say "wave2 complete"
