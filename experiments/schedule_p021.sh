#!/usr/bin/env bash
# P021 completion watcher: waits for the runner process to exit, then writes
# the frozen analysis and appends the budget ledger — same post-processing the
# P018->P019->P020 chain performed per cohort.
set -u
cd "$(dirname "$0")"
ROOT="$(pwd)"
DIR="$ROOT/info_contract_aesgcm_random_p021_20261102"
LOG="$ROOT/chain_p021.log"

log() { echo "$(date -Is) $*" >> "$LOG"; }

log "watcher start; waiting for run_p021_aesgcm.py to exit"
while ps -eo args= | grep -qx "python3 run_p021_aesgcm.py"; do sleep 120; done
log "runner exited"

python3 "$ROOT/analyze_random_cohort.py" "$DIR" > "$DIR/analysis_p021.txt" 2>&1 \
  && log "analysis written" || log "analysis FAILED"
python3 "$ROOT/append_budget_to_ledger.py" "$DIR" >> "$LOG" 2>&1 \
  || log "budget append FAILED"
tail -25 "$DIR/analysis_p021.txt" >> "$LOG" 2>/dev/null
log "watcher finished"
