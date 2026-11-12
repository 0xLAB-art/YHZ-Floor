#!/usr/bin/env bash
# Wait for P023's frozen analysis, then regenerate the clustering analysis.
set -u
cd "$(dirname "$0")"
ROOT="$(pwd)"
LOG="$ROOT/chain_position_cluster.log"
A23="$ROOT/info_contract_aesgcm_random_p023_20261103/analysis_p023.txt"

log() { echo "$(date -Is) $*" >> "$LOG"; }

log "position-cluster watcher start; waiting for $A23"
while [ ! -s "$A23" ]; do sleep 120; done
log "P023 analysis present; running clustering analysis"
python3 "$ROOT/position_cluster_p021_p023.py" >> "$LOG" 2>&1 \
  && log "clustering written" || log "clustering FAILED"
log "watcher finished"
