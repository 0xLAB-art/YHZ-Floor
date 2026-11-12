#!/usr/bin/env bash
# Wait for both P024 arm analyses, then write the P022-vs-P024 comparison.
set -u
cd "$(dirname "$0")"
ROOT="$(pwd)"
LOG="$ROOT/chain_compare_p022_p024.log"
A="$ROOT/info_contract_aesgcm_p024a_20261103/analysis_p024a.txt"
B="$ROOT/info_contract_aesgcm_p024b_20261103/analysis_p024b.txt"

log() { echo "$(date -Is) $*" >> "$LOG"; }

log "comparison watcher start; waiting for both P024 analyses"
while [ ! -s "$A" ] || [ ! -s "$B" ]; do sleep 120; done
log "P024 analyses present; writing comparison"
python3 "$ROOT/compare_p022_p024.py" >> "$LOG" 2>&1 \
  && log "comparison written" || log "comparison FAILED"
log "watcher finished"
