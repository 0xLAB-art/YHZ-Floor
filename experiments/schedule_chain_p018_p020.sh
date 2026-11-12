#!/usr/bin/env bash
# Serialized chain: P018 (AES-GCM) -> P019 (ChaCha20-Poly1305) -> P020 (AES-GCM-SIV).
#
# The three cohorts are built to run together but must never share the key
# concurrently: P014/P016/P017 all state that concurrency on one AgentRouter key
# is a failure channel (429 -> terminal provider failure) that leaks into cell
# denominators. So the provider calls are serialized and only the engineering
# was done in parallel.
#
# Liveness uses exact argv lines (`grep -qx`), never a bare name: a
# `pgrep -f run_p017_aesgcm` also matches any shell that merely mentions it.
set -u
cd "$(dirname "$0")"
ROOT="$(pwd)"
LOG="$ROOT/chain_p018_p020.log"

log() { echo "$(date -Is) $*" >> "$LOG"; }

p017_running() {
  ps -eo args= | grep -qx "python3 run_p017_aesgcm.py" && return 0
  ps -eo args= | grep -qx "bash schedule_p017.sh" && return 0
  return 1
}

run_cohort() {
  local dir="$1" cmd="$2" tag="$3"
  log "$tag start"
  ( cd "$dir" && eval "$cmd" ) >> "$LOG" 2>&1
  local rc=$?
  log "$tag runner exit rc=$rc"
  python3 "$ROOT/analyze_random_cohort.py" "$dir" > "$dir/analysis_${tag,,}.txt" 2>&1
  log "$tag analysis written to analysis_${tag,,}.txt"
  python3 "$ROOT/append_budget_to_ledger.py" "$dir" >> "$LOG" 2>&1 \
    || log "$tag budget append FAILED"
  tail -25 "$dir/analysis_${tag,,}.txt" >> "$LOG"
}

log "chain start; waiting for P017 to exit"
while p017_running; do sleep 60; done
log "P017 finished; starting P018"

run_cohort "$ROOT/info_contract_aesgcm_random_20261102" \
           "python3 run_p018_aesgcm.py" "P018"

run_cohort "$ROOT/info_contract_chachapoly_random_20261102" \
           "python3 ../run_modern_aead_cohort.py ." "P019"

run_cohort "$ROOT/info_contract_gcmsiv_random_20261102" \
           "python3 ../run_modern_aead_cohort.py ." "P020"

log "chain finished"
