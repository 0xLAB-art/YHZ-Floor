#!/usr/bin/env bash
# P024 chain: P022 paired re-run on the repaired transport.
#
# Serialization: one key never carries two cohorts. This chain waits for the
# P023 runner to exit AND its analysis to be written, then probes the token
# floor on a spent P022 instance, registers both arms, and runs them serially.
set -u
cd "$(dirname "$0")"
ROOT="$(pwd)"
LOG="$ROOT/chain_p024.log"

log() { echo "$(date -Is) $*" >> "$LOG"; }
wait_for() { while ps -eo args= | grep -qx "$1"; do sleep 120; done; }

log "chain start; waiting for P023 runner + its analysis"
wait_for "python3 run_p023_aesgcm.py"
A23="$ROOT/info_contract_aesgcm_random_p023_20261103/analysis_p023.txt"
while [ ! -s "$A23" ]; do sleep 120; done
log "P023 analysis present; probing the P024 token floor"

python3 "$ROOT/probe_p024_floor.py" >> "$LOG" 2>&1 || { log "probe FAILED"; exit 1; }
FLOOR="$(python3 -c 'import json;print(json.load(open("probe_p024_floor.json"))["decided_floor"])')" \
  || { log "probe read FAILED"; exit 1; }
log "probe decided floor=$FLOOR"

python3 "$ROOT/build_p024_registration.py" --arm a --floor "$FLOOR" >> "$LOG" 2>&1 \
  || { log "registration a FAILED"; exit 1; }
python3 "$ROOT/build_p024_registration.py" --arm b --floor "$FLOOR" >> "$LOG" 2>&1 \
  || { log "registration b FAILED"; exit 1; }
log "both arms registered"

for arm in a b; do
  DIR="$ROOT/info_contract_aesgcm_p024${arm}_20261103"
  log "P024$arm start"
  ( cd "$DIR" && python3 run_p024_arm.py ) >> "$LOG" 2>&1
  RC=$?
  log "P024$arm runner exit rc=$RC"
  python3 "$ROOT/analyze_random_cohort.py" "$DIR" > "$DIR/analysis_p024$arm.txt" 2>&1 \
    && log "P024$arm analysis written" || log "P024$arm analysis FAILED"
  python3 "$ROOT/append_budget_to_ledger.py" "$DIR" >> "$LOG" 2>&1 \
    || log "P024$arm budget append FAILED"
done

log "chain finished"
