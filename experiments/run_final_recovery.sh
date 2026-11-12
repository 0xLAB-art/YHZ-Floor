#!/usr/bin/env bash
# FINAL recovery — author constraints v3 (2026-11-03 21:00):
#   * last $50; gpt-6-astra BANNED (author directive after the $99 burn)
#   * substitute label: gpt-5.6-sol for all astra-labeled cohorts
#   * concurrency 6; quota sentinel watches EACH cohort's own recovery log
#   * abort everything on 6 quota-403s in the active cohort's log tail
set -u
cd "$(dirname "$0")"
LOG="FINAL_RECOVERY_20261103.log"
SUB="gpt-5.6-sol"
say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }

quota_dead() {  # $1 = the cohort's own recovery log
  local n; n=$(grep -c "quota is not enough" "$1" 2>/dev/null || echo 0)
  [ "$n" -ge 6 ]
}

run_cohort() {  # $1 name, $2 dir, $3 workers, $4 label, $5 script, $6 logname
  say "start $1 (label $4, workers $3)"
  ( cd "$2" && AGENTROUTER_LABEL_MODEL=$4 APINEX_LABEL_MODEL=$4 \
    ACTS_FAILURE_LOG=failure_log.jsonl ACTS_CONCURRENCY=$3 \
    python3 -u "$5" >> "$6" 2>&1 )
  if quota_dead "$2/$6"; then
    say "QUOTA SENTINEL: quota-403s in $1's log — ABORTING to protect the last \$50"
    exit 3
  fi
  say "done $1"
}

# boundary notes for the label split
write_note() {  # $1 dir, $2 primary label, $3 boundary
  cat > "$1/RECOVERY_LABEL_SUBSTITUTION.md" << NOTE
# Label substitution in the recovery pass (author-directed, 2026-11-03)

The registered label for this cohort is \`$2\`. Its recovery pairs ran on
\`$SUB\` because the author banned \`gpt-6-astra\` for cost after two quota
exhaustions. Rows 1..$3 of results.jsonl are primary-label sessions; rows
after line $3 are substitute-label sessions. The unified analysis reports
the two label groups separately; no acceptance number mixes them.
NOTE
}

B=$(wc -l < info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103/results.jsonl 2>/dev/null || echo 0)
run_cohort "P023" info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103 6 $SUB run_p023_aesgcm.py recovery_p023.log
write_note info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103 "gpt-6-astra" "$B"

B=$(wc -l < info_contract_aesgcm_c2_floor8000_p026_20261103/results.jsonl 2>/dev/null || echo 0)
run_cohort "P026" info_contract_aesgcm_c2_floor8000_p026_20261103 6 $SUB run_p026_c2_floor8000.py recovery_p026.log
write_note info_contract_aesgcm_c2_floor8000_p026_20261103 "gpt-6-astra" "$B"

B=$(wc -l < info_contract_aesgcm_random_20261102__rerun_ar_20261103/results.jsonl 2>/dev/null || echo 0)
run_cohort "P018" info_contract_aesgcm_random_20261102__rerun_ar_20261103 6 $SUB run_p018_aesgcm.py recovery_p018.log
write_note info_contract_aesgcm_random_20261102__rerun_ar_20261103 "gpt-6-astra" "$B"

say "P017 (3 pairs, shards)"
python3 -u shard_base_main.py info_contract_aesgcm_p017_20261102__rerun_ar_20261103 3 >> recovery_p017.log 2>&1
quota_dead recovery_p017.log && { say "QUOTA SENTINEL abort"; exit 3; }
say "done P017"

say "P016 arm top-up (1 pair, original label gpt-6.1-sol kept)"
python3 -u rerun_p016_arm.py gpt_6_1_sol >> recovery_p016a.log 2>&1
say "done P016 arm"

say "final analysis + markers"
python3 -u analyze_rerun_vs_original.py >> "$LOG" 2>&1 || true
python3 -u build_paper_evidence_20261103.py >> "$LOG" 2>&1 || true
echo "[$(date -u +%H:%M:%SZ)] wave3 complete (final recovery)" >> WAVE3_20261103.log
say "FINAL RECOVERY COMPLETE"
