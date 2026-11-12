#!/usr/bin/env bash
# P022 chain: waits for P021 to fully finish (runner gone AND analysis written
# by schedule_p021.sh), then runs arm a (gpt-6.1-sol), analyzes, then arm b
# (gpt-5.6-sol), analyzes, then appends both to the budget ledger.
#
# Serialization rule: one key never carries two cohorts. Liveness uses exact
# argv lines (grep -qx), never a bare name.
set -u
cd "$(dirname "$0")"
ROOT="$(pwd)"
LOG="$ROOT/chain_p022.log"

log() { echo "$(date -Is) $*" >> "$LOG"; }

wait_for() {  # wait until a process matching the exact argv line is gone
  while ps -eo args= | grep -qx "$1"; do sleep 120; done
}

log "chain start; waiting for P021 runner + its analysis"
wait_for "python3 run_p021_aesgcm.py"
A21="$ROOT/info_contract_aesgcm_random_p021_20261102/analysis_p021.txt"
while [ ! -s "$A21" ]; do sleep 120; done
log "P021 analysis present; starting P022a"

DIRA="$ROOT/info_contract_aesgcm_p022a_20261102"
DIRB="$ROOT/info_contract_aesgcm_p022b_20261102"

log "P022a start"
( cd "$DIRA" && python3 run_p022a_aesgcm.py ) >> "$LOG" 2>&1
log "P022a runner exit rc=$?"
python3 "$ROOT/analyze_random_cohort.py" "$DIRA" > "$DIRA/analysis_p022a.txt" 2>&1 \
  && log "P022a analysis written" || log "P022a analysis FAILED"

log "P022b start"
( cd "$DIRB" && python3 run_p022b_aesgcm.py ) >> "$LOG" 2>&1
log "P022b runner exit rc=$?"
python3 "$ROOT/analyze_random_cohort.py" "$DIRB" > "$DIRB/analysis_p022b.txt" 2>&1 \
  && log "P022b analysis written" || log "P022b analysis FAILED"

python3 "$ROOT/append_budget_to_ledger.py" "$DIRA" >> "$LOG" 2>&1 || log "budget append A FAILED"
python3 "$ROOT/append_budget_to_ledger.py" "$DIRB" >> "$LOG" 2>&1 || log "budget append B FAILED"

log "chain finished"
