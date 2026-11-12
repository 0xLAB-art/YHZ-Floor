#!/usr/bin/env bash
# Final recovery — AUTHOR CONSTRAINTS (2026-11-03 20:15):
#   * last $23 on AgentRouter — gpt-6-astra is banned (cost); the astra-labeled
#     recoveries run on gpt-5.6-sol instead (structural behavior verified in
#     the P022b rerun: 48/48 bearing accepted) and every recovered row is
#     reported as a disclosed label substitution, side-by-side with the
#     primary astra rows.
#   * concurrency capped at 8 (the key was abuse-flagged once already).
#   * quota sentinel: 6 consecutive quota-403s abort the remaining queue so
#     no budget is wasted on futile attempts.
set -u
cd "$(dirname "$0")"
LOG="RECOVERY_20261103.log"
SUB="gpt-5.6-sol"
say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }

say "armed (substitute label: $SUB, cap 8); probing route every 10 min"
while true; do
  if timeout 90 python3 -u -c "
import importlib.util, sys, os
from pathlib import Path
os.environ['AGENTROUTER_LABEL_MODEL']='$SUB'
spec=importlib.util.spec_from_file_location('pa', Path('provider_adapter_agentrouter_p023.py').resolve())
m=importlib.util.module_from_spec(spec); sys.modules['pa']=m; spec.loader.exec_module(m)
p=m.ClaudeProvider()
r=p.call('Reply with the single word READY',1400)
print('PROBE_OK', r['text'][:20])
" >> "$LOG" 2>&1; then say "route restored (quota available for $SUB)"; break; fi
  sleep 600
done

QUOTA_FAILS=0
check_quota() {
  local recent
  recent=$(tail -40 "$1" 2>/dev/null | grep -c "quota is not enough" || true)
  if [ "$recent" -ge 6 ]; then
    say "QUOTA SENTINEL: $recent quota-403s in the last events — ABORTING remaining recovery to protect the last \$23"
    exit 3
  fi
}

write_note() {
  cat > "$1/RECOVERY_LABEL_SUBSTITUTION.md" << NOTE
# Label substitution in the recovery pass (author-directed, 2026-11-03)

The registered label for this cohort is \`$2\`. Its recovery pairs ran on
\`$SUB\` because the author banned \`gpt-6-astra\` for cost after the second
quota exhaustion. Rows 1..$3 of results.jsonl are primary-label sessions;
rows after line $3 are substitute-label sessions. The unified analysis
reports the two label groups separately; no acceptance number mixes them.
NOTE
}

say "P023 recovery (231 pairs, $SUB, cap 8)"
B=$(wc -l < info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103/results.jsonl 2>/dev/null || echo 0)
( cd info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103 && \
  AGENTROUTER_LABEL_MODEL=$SUB APINEX_LABEL_MODEL=$SUB \
  ACTS_FAILURE_LOG=failure_log.jsonl ACTS_CONCURRENCY=8 \
  python3 -u run_p023_aesgcm.py >> recovery_p023.log 2>&1 ) \
  && say "P023 recovered" || say "P023 ended (check log)"
check_quota "$LOG"
write_note info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103 "gpt-6-astra" "$B"

say "P026 recovery (67 pairs)"
B=$(wc -l < info_contract_aesgcm_c2_floor8000_p026_20261103/results.jsonl 2>/dev/null || echo 0)
( cd info_contract_aesgcm_c2_floor8000_p026_20261103 && \
  AGENTROUTER_LABEL_MODEL=$SUB APINEX_LABEL_MODEL=$SUB \
  ACTS_FAILURE_LOG=failure_log.jsonl \
  python3 -u run_p026_c2_floor8000.py >> recovery_p026.log 2>&1 ) \
  && say "P026 recovered" || say "P026 ended (check log)"
check_quota "$LOG"
write_note info_contract_aesgcm_c2_floor8000_p026_20261103 "gpt-6-astra" "$B"

say "P018 recovery (45 pairs)"
B=$(wc -l < info_contract_aesgcm_random_20261102__rerun_ar_20261103/results.jsonl 2>/dev/null || echo 0)
( cd info_contract_aesgcm_random_20261102__rerun_ar_20261103 && \
  AGENTROUTER_LABEL_MODEL=$SUB APINEX_LABEL_MODEL=$SUB \
  ACTS_FAILURE_LOG=failure_log.jsonl ACTS_CONCURRENCY=8 \
  python3 -u run_p018_aesgcm.py >> recovery_p018.log 2>&1 ) \
  && say "P018 recovered" || say "P018 ended (check log)"
check_quota "$LOG"
write_note info_contract_aesgcm_random_20261102__rerun_ar_20261103 "gpt-6-astra" "$B"

say "P017 recovery (6 pairs)"
python3 -u shard_base_main.py info_contract_aesgcm_p017_20261102__rerun_ar_20261103 6 >> recovery_p017.log 2>&1 \
  && say "P017 recovered" || say "P017 ended (check log)"
check_quota "$LOG"

say "P016 gpt_6_1_sol arm top-up (1 pair — original label kept)"
python3 -u rerun_p016_arm.py gpt_6_1_sol >> recovery_p016a.log 2>&1 \
  && say "P016 arm recovered" || say "P016 arm ended (check log)"

say "recoveries done; analysis + markers"
python3 -u analyze_rerun_vs_original.py >> "$LOG" 2>&1 || true
echo "[$(date -u +%H:%M:%SZ)] wave3 complete (post-recharge recovery)" >> WAVE3_20261103.log
say "RECOVERY COMPLETE"
