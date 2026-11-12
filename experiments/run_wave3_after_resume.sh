#!/usr/bin/env bash
# Wave-3: the two P016 labels arms (floor 2800, matched re-runs), chained after
# the master resume sequence completes (salvage -> queue -> A3b -> P026).
# One arm at a time on the shared key. Log: WAVE3_20261103.log.
set -u
cd "$(dirname "$0")"
LOG="WAVE3_20261103.log"
say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }

say "wave3 armed; waiting for 'resume sequence complete' in RESUME_20261103.log"
while ! grep -q "resume sequence complete" RESUME_20261103.log 2>/dev/null; do
  sleep 300
done
say "resume sequence finished; starting P016 labels arms (floor 2800, matched)"

for arm in gpt_6_1_sol gpt_5_6_sol; do
  clone="info_contract_aesgcm_labels_${arm}__rerun_ar_20261103"
  if [ -f "$clone/summary.json" ]; then
    say "skip $arm (already complete)"
    continue
  fi
  say "start $arm"
  if python3 -u rerun_p016_arm.py "$arm" >> "$LOG" 2>&1; then
    say "done $arm"
  else
    say "FAIL $arm (see $clone logs)"
  fi
done
say "wave3 complete"
