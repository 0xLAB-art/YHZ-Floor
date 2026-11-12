#!/usr/bin/env bash
# Wait for P023's frozen analysis, then write the P021-vs-P023 comparison.
# Separate from schedule_p023.sh so the running watcher is never modified.
set -u
cd "$(dirname "$0")"
ROOT="$(pwd)"
LOG="$ROOT/chain_compare_p021_p023.log"
A23="$ROOT/info_contract_aesgcm_random_p023_20261103/analysis_p023.txt"

log() { echo "$(date -Is) $*" >> "$LOG"; }

log "comparison watcher start; waiting for $A23"
while [ ! -s "$A23" ]; do sleep 120; done
log "P023 analysis present; writing comparison"
python3 "$ROOT/compare_p021_p023.py" >> "$LOG" 2>&1 \
  && log "comparison written" || log "comparison FAILED"
log "watcher finished"
