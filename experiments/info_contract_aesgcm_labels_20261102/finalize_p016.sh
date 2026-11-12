#!/usr/bin/env bash
# Completion-triggered finalizer for P016 (both labels).
#
# Liveness is tested against EXACT argv lines, never a bare name: the P014
# finalizer stalled because `pgrep -f run_p014_aesgcm` also matched unrelated
# shells that merely mentioned the script (monitoring commands included).
#
# Fires when: the scheduler has logged its finish line AND no P016 process is
# left. Then writes analysis_p016.txt and appends each label's calls to the
# ledger. P017's scheduler is independent of this one and starts on its own.
set -u
cd "$(dirname "$0")"
NS="$(pwd)"
LOG="$NS/finalize.log"
OUT="$NS/analysis_p016.txt"
DEADLINE=$(( $(date +%s) + 43200 ))

log() { echo "$(date -Is) $*" >> "$LOG"; }

p016_alive() {
  ps -eo args= | grep -qx "python3 run_p016_aesgcm.py" && return 0
  ps -eo args= | grep -qx "bash schedule_p016.sh" && return 0
  return 1
}

slots_total() {
  python3 - <<'PY'
import json
from pathlib import Path
n = 0
for slug in ("gpt_6_1_sol", "gpt_5_6_sol"):
    p = Path(slug) / "results.jsonl"
    if p.exists():
        seen = set()
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                seen.add((r["seed"], r["cell"]))
        n += len(seen)
print(n)
PY
}

log "finalizer start; waiting for P016 scheduler + both labels"
while :; do
  if ! p016_alive && grep -q "scheduler finished" scheduler.log 2>/dev/null; then
    break
  fi
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    log "TIMEOUT reached; analysing what exists"
    break
  fi
  sleep 60
done

log "P016 done; slots recorded=$(slots_total)/128"
{
  echo "# P016 AES-GCM cross-label cohort analysis"
  echo "# generated: $(date -Is)"
  echo "# estimator: analyze_p016.py (frozen before either label completed)"
  echo "# same frozen AES-GCM runner, same floor 2800 as P014, labels differ"
  echo
  python3 analyze_p016.py 2>&1
} > "$OUT"
log "analysis written to $OUT"

for slug in gpt_6_1_sol gpt_5_6_sol; do
  python3 ../append_budget_to_ledger.py "$NS/$slug" >> "$LOG" 2>&1 \
    || log "budget append failed for $slug"
done

tail -40 "$OUT" >> "$LOG"
