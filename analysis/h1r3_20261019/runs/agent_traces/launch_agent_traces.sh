#!/usr/bin/env bash
set -uo pipefail

ROOT="sp2027/analysis/h1r3_20261019"
DIR="$ROOT/runs/agent_traces"

mkdir -p "$DIR"
echo "running 5 agent trace scripts from: $DIR"

python3 "$DIR/run_agent_01_trace_original_h1_pilot.py" || true
python3 "$DIR/run_agent_02_trace_executed_artifact_identity.py" || true
python3 "$DIR/run_agent_03_trace_scorer_and_instrument_defects.py" || true
python3 "$DIR/run_agent_04_trace_evaluator_boundary_proposal.py" || true
python3 "$DIR/run_agent_05_trace_tasks_seeds_budget_limits.py" || true

echo "---- trace summary ----"
for f in "$DIR"/agent_*_trace_*.json; do
  if [ -f "$f" ]; then
    python3 - "$f" <<'PY'
from pathlib import Path
import json, sys
p = Path(sys.argv[1])
d = json.loads(p.read_text())
print("agent:", d.get("agent"))
print("provider_calls:", d.get("provider_calls"))
print("critical_issues_traced:", len(d.get("critical_issues_traced", [])))
print("completed_utc:", d.get("completed_utc"))
PY
    echo "----------------------"
  fi
done

echo "done"
