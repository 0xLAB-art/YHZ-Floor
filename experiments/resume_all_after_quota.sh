#!/usr/bin/env bash
# Master resume after the 2026-11-03 17:49 AgentRouter quota block.
# Probes the route until it works again, then resumes everything in order:
#   1. gcmsiv salvage (its 3 unfinished shards resume in place, then merge)
#   2. the 14-cohort rerun queue (restart-safe; skips completed clones)
#   3. A3b transport recovery (18 pairs; quarantined first attempt kept as evidence)
#   4. P026 C2 floor-sensitivity (96 sessions, floor 8000; quarantined first attempt kept)
# All logged to RESUME_20261103.log. Safe to kill and rerun at any point.
set -u
cd "$(dirname "$0")"
LOG="RESUME_20261103.log"
GC="info_contract_gcmsiv_random_20261102__rerun_ar_20261103"
say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }

say "resume armed; probing route every 10 min until quota/key restored"
while true; do
  if timeout 90 python3 -u -c "
import importlib.util, os, sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('pa', Path('provider_adapter_agentrouter_p023.py').resolve())
m=importlib.util.module_from_spec(spec); sys.modules['pa']=m; spec.loader.exec_module(m)
p=m.ClaudeProvider()
r=p.call('Reply with the single word READY',1400)
print('PROBE_OK', r['text'][:20])
" >> "$LOG" 2>&1; then
    say "route restored"
    break
  fi
  sleep 600
done

# 1) gcmsiv salvage
if [ ! -f "$GC/summary.json" ]; then
  say "salvaging gcmsiv (resume incomplete shards, then merge)"
  for pass in 1 2; do
    for s in "$GC"/shard_00 "$GC"/shard_01 "$GC"/shard_04; do
      python3 -u run_modern_aead_cohort.py "$s" >> "$LOG" 2>&1 || say "warn shard rerun exit != 0 ($s)"
    done
    python3 - << PY >> "$LOG" 2>&1
import json, sys
sys.path.insert(0, '.')
from pathlib import Path
from rerun_ar_clone import merge_shards
gc = Path('$GC')
reg = json.loads((gc/'_REGISTRATION.json').read_text())
shards = sorted(p for p in gc.glob('shard_*') if p.is_dir())
s = merge_shards(gc, shards, reg['protocol'], reg)
print('merged sessions', s['sessions'], 'planned 32')
PY
    n=$(python3 -c "import json;print(json.load(open('$GC/summary.json'))['sessions'])" 2>/dev/null || echo 0)
    if [ "$n" = "32" ]; then say "gcmsiv complete ($n/32)"; break; fi
    say "gcmsiv still incomplete ($n/32); pass $pass done, retrying"
  done
else
  say "skip gcmsiv salvage (summary exists)"
fi

# 2) queue
say "relaunching the 14-cohort rerun queue (restart-safe)"
bash rerun_ar_queue.sh >> "$LOG" 2>&1 && say "queue finished" || say "queue exited nonzero (see log)"

# 3) A3b
if [ ! -f info_contract_aesgcm_random_p021ar_20261103/amendment_a3b/summary.json ]; then
  say "running A3b transport recovery"
  ( cd info_contract_aesgcm_random_p021ar_20261103 && python3 -u run_p021ar_a3b_topup.py ) >> "$LOG" 2>&1 \
    && say "A3b done" || say "A3b FAILED"
else
  say "skip A3b (already complete)"
fi

# 4) P026
if [ ! -f info_contract_aesgcm_c2_floor8000_p026_20261103/summary.json ]; then
  say "running P026 C2 floor-sensitivity"
  ( cd info_contract_aesgcm_c2_floor8000_p026_20261103 && python3 -u run_p026_c2_floor8000.py ) >> "$LOG" 2>&1 \
    && say "P026 done" || say "P026 FAILED"
else
  say "skip P026 (already complete)"
fi

say "resume sequence complete"
