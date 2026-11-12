#!/usr/bin/env bash
# Sequential re-run queue for the 16 remaining transport-damaged cohorts.
#
# One cohort at a time, on purpose: every cohort in this queue shares one
# AgentRouter key, and the P021 lesson is that concurrency without pacing turns
# into provider failures that then look like science.
#
# Skips any cohort whose clone already carries a summary.json, so the queue can be
# restarted safely. Never touches the original namespace.
set -u
cd "$(dirname "$0")"

LOG="RERUN_QUEUE_20261103.log"
P021="info_contract_aesgcm_random_p021ar_20261103"

say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }

say "queue start; waiting for $P021 to finish"
while [ ! -f "$P021/summary.json" ]; do
  if ! pgrep -f "[r]un_p021ar.py" >/dev/null; then
    say "P021AR process gone; summary.json present=$( [ -f "$P021/summary.json" ] && echo yes || echo no )"
    break
  fi
  sleep 60
done
say "P021AR finished or stopped; starting cohort queue"

QUEUE=(
  info_contract_gcmsiv_random_20261102
  info_contract_chachapoly_random_20261102
  info_contract_aesgcm_random_20261102
  info_contract_aesgcm_20261102
  info_contract_aesgcm_p017_20261102
  info_contract_aesgcm_p022a_20261102
  info_contract_aesgcm_random_p023_20261103
  info_contract_label3_n32_20261101
  info_contract_aesgcm_p022b_20261102
  info_contract_aesgcm_p024b_20261103
  info_contract_label2_20261025
  info_contract_label4_20261030
  info_contract_label5_20261030
  info_contract_label5r_20261030
)

for c in "${QUEUE[@]}"; do
  clone="${c}__rerun_ar_20261103"
  if [ -f "$clone/summary.json" ]; then
    say "skip $c (already complete)"
    continue
  fi
  say "start $c"
  if python3 -u rerun_ar_clone.py "$c" >> "$LOG" 2>&1; then
    if [ -f "$clone/summary.json" ]; then
      fail=$(python3 -c "import json;print(json.load(open('$clone/summary.json'))['provider_failures'])" 2>/dev/null)
      say "done $c provider_failures=$fail"
    else
      say "warn $c exited 0 without summary.json"
    fi
  else
    say "FAIL $c (see $clone/runner_console.log)"
  fi
done

say "queue complete"
