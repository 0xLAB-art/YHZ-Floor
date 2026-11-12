#!/usr/bin/env bash
# Sequential P017 scheduler: start only after P016 has fully finished.
#
# Liveness is tested against the EXACT argv lines (`grep -qx`), never a bare
# name: a `pgrep -f run_p016_aesgcm` also matches any shell that merely mentions
# the script, which is the bug that stalled the P014 finalizer.
set -u
cd "$(dirname "$0")"
NS="$(pwd)"
LOG="$NS/scheduler.log"

log() { echo "$(date -Is) $*" >> "$LOG"; }

p016_running() {
  ps -eo args= | grep -qx "python3 run_p016_aesgcm.py" && return 0
  ps -eo args= | grep -qx "bash schedule_p016.sh" && return 0
  return 1
}

log "scheduler start; waiting for P016 (both labels) to finish"

while p016_running; do sleep 60; done

log "P016 finished; starting P017 at floor 4200"
python3 run_p017_aesgcm.py >> "$NS/runner_console.log" 2>&1
rc=$?
log "P017 exited rc=$rc"

# Analysis and ledger close-out, on success or not, so a partial cohort is still
# reported rather than left unread.
python3 analyze_p017.py > "$NS/analysis_p017.txt" 2>&1
log "analysis written to analysis_p017.txt"
python3 ../append_budget_to_ledger.py "$NS" >> "$LOG" 2>&1 || log "budget append FAILED"
tail -20 "$NS/analysis_p017.txt" >> "$LOG"
