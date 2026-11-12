#!/usr/bin/env bash
# Completion-triggered finalizer for P014.
#
# Waits until the P014 launcher process has exited AND every registered
# (seed, cell) slot is present, then runs the frozen analysis exactly once and
# writes its output next to the cohort. Nothing about the design, the cells or
# the estimator can change here: this script only decides WHEN the frozen
# analysis may be read.
#
# Exit conditions (each logged, never silent):
#   COMPLETE     64/64 slots present -> analysis run, output saved
#   PARTIAL_EXIT process gone but slots missing -> analysis run on what exists,
#                clearly labelled PARTIAL, with the missing slot count
#   TIMEOUT      12 h cap -> analysis run on what exists, labelled TIMEOUT
set -u
cd "$(dirname "$0")"
NS="$(pwd)"
LOG="$NS/finalize.log"
OUT="$NS/analysis_p014.txt"
RESULTS="$NS/results.jsonl"
DEADLINE=$(( $(date +%s) + 43200 ))
LABEL="COMPLETE"

log() { echo "$(date -Is) $*" >> "$LOG"; }

# Liveness by PID, not by name. A bare `pgrep -f run_p014_aesgcm` also matches
# any shell whose argv merely mentions the script (a monitoring `tail`/`grep`
# does), which made this finalizer wait forever. RUN_PID is written by the
# launcher; the fallback requires the exact interpreter+script pair.
p014_alive() {
  local pid
  pid="$(cat "$NS/RUN_PID" 2>/dev/null | tr -dc '0-9')"
  if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then return 0; fi
  pgrep -f "python3 run_p014_aesgcm\.py" > /dev/null 2>&1
}

slot_count() {
  python3 - "$RESULTS" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
if not p.exists():
    print(0); raise SystemExit
seen = set()
for line in p.read_text().splitlines():
    if line.strip():
        r = json.loads(line)
        seen.add((r["seed"], r["cell"]))
print(len(seen))
PY
}

log "finalizer start; waiting for the 64 registered slots"

while :; do
  slots="$(slot_count)"
  if p014_alive; then
    if [ "$slots" -ge 64 ]; then
      # process still alive just after the last row: wait for a clean exit
      sleep 30
      p014_alive || break
    fi
  else
    if [ "$slots" -lt 64 ]; then LABEL="PARTIAL_EXIT"; fi
    break
  fi
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then LABEL="TIMEOUT"; break; fi
  sleep 60
done

slots="$(slot_count)"
log "proceeding with label=$LABEL slots=$slots/64"

{
  echo "# P014 AES-GCM cohort analysis"
  echo "# state: $LABEL   slots: $slots/64   generated: $(date -Is)"
  echo "# estimator: analyze_p014.py (frozen before cohort completion);"
  echo "#            helpers loaded by path from analyze_p011.py"
  echo
  python3 analyze_p014.py 2>&1
} > "$OUT"

log "analysis written to $OUT"

# prereg §3: every call's tokens/cost goes to the ledger. Idempotent, so this
# catches sessions completed after the last manual append.
python3 ../append_budget_p014.py >> "$LOG" 2>&1 || log "budget append FAILED (see above)"

tail -20 "$OUT" >> "$LOG"
