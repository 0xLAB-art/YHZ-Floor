#!/usr/bin/env bash
# Parallel repair wave — 2026-11-03. Replaces the sequential queue: every
# remaining cohort runs concurrently, sized to keep the route's total
# in-flight sessions near 45. Two batches with a transport-failure gate
# between them. Log: PARALLEL_WAVE_20261103.log
set -u
cd "$(dirname "$0")"
LOG="PARALLEL_WAVE_20261103.log"
say() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }

# ---- Batch 1: the big cohorts -------------------------------------------
# P018: resume its clone's 35 judged rows via its own launcher at concurrency 8
say "P018 resume (launcher, ACTS_CONCURRENCY=8)"
( cd info_contract_aesgcm_random_20261102__rerun_ar_20261103 && \
  AGENTROUTER_LABEL_MODEL=gpt-6-astra APINEX_LABEL_MODEL=gpt-6-astra \
  ACTS_FAILURE_LOG=failure_log.jsonl ACTS_CONCURRENCY=8 \
  nohup python3 -u run_p018_aesgcm.py >> ../P018_PARALLEL.log 2>&1 & )

# P023 (384) and P024b (96) via their launchers through the clone (fast path)
say "P023 + P024b clones (launchers, concurrency 8)"
nohup python3 -u rerun_ar_clone.py info_contract_aesgcm_random_p023_20261103 >> "$LOG" 2>&1 &
nohup python3 -u rerun_ar_clone.py info_contract_aesgcm_p024b_20261103 >> "$LOG" 2>&1 &

# P022a/b, label3 — sharded base.main
say "P022a(6) P022b(6) label3(8) shards"
nohup python3 -u rerun_ar_clone.py info_contract_aesgcm_p022a_20261102 --shards 6 >> "$LOG" 2>&1 &
nohup python3 -u rerun_ar_clone.py info_contract_aesgcm_p022b_20261102 --shards 6 >> "$LOG" 2>&1 &
nohup python3 -u rerun_ar_clone.py info_contract_label3_n32_20261101 --shards 8 >> "$LOG" 2>&1 &
say "batch 1 launched (in-flight ~40)"

# ---- gate: transport-failure rate check after 3 min ----------------------
sleep 180
RATE=$(python3 - << 'PY'
import json, time
from pathlib import Path
now = time.time(); bad = ok = 0
for d in Path('.').glob('*__rerun_ar_20261103'):
    rp = d / 'results.jsonl'
    if not rp.exists(): continue
    for line in rp.read_text().splitlines()[-400:]:
        try: r = json.loads(line)
        except Exception: continue
        s = r.get('status')
        if s in ('HTTP_ERROR', 'TIMEOUT'): bad += 1
        elif s in ('SUCCESS', 'ORACLE_FAIL'): ok += 1
print(f"{bad / max(ok + bad, 1):.3f}")
PY
)
say "transport-failure rate after 3 min: $RATE"
HOLD=$(python3 -c "print(1 if float('$RATE') > 0.15 else 0)")
if [ "$HOLD" = "1" ]; then
  say "FAILURE RATE HIGH — batch 2 HELD; batch 1 continues alone"
else
  # ---- Batch 2: the small cohorts + amendments + P016 arms ---------------
  say "batch 2: P014(4) P017(4) label2(2) label4(2) label5(2) label5r(2)"
  nohup python3 -u rerun_ar_clone.py info_contract_aesgcm_20261102 --shards 4 >> "$LOG" 2>&1 &
  nohup python3 -u rerun_ar_clone.py info_contract_aesgcm_p017_20261102 --shards 4 >> "$LOG" 2>&1 &
  nohup python3 -u rerun_ar_clone.py info_contract_label2_20261025 --shards 2 >> "$LOG" 2>&1 &
  nohup python3 -u rerun_ar_clone.py info_contract_label4_20261030 --shards 2 >> "$LOG" 2>&1 &
  nohup python3 -u rerun_ar_clone.py info_contract_label5_20261030 --shards 2 >> "$LOG" 2>&1 &
  nohup python3 -u rerun_ar_clone.py info_contract_label5r_20261030 --shards 2 >> "$LOG" 2>&1 &
  say "amendments: A3b(3) P026(6); P016 arms(3+3)"
  nohup python3 -u rerun_ar_clone.py info_contract_aesgcm_c2_floor8000_p026_20261103 >> "$LOG" 2>&1 &
  nohup python3 -u rerun_ar_clone.py info_contract_aesgcm_random_p021ar_20261103 >> "$LOG" 2>&1 &
  nohup python3 -u rerun_p016_arm.py gpt_6_1_sol >> "$LOG" 2>&1 &
  nohup python3 -u rerun_p016_arm.py gpt_5_6_sol >> "$LOG" 2>&1 &
  say "batch 2 launched"
fi

# ---- wait for everything -------------------------------------------------
wait
say "all wave jobs returned; writing analysis"
python3 -u analyze_rerun_vs_original.py >> "$LOG" 2>&1 || true
# markers for the monitors
echo "[$(date -u +%H:%M:%SZ)] resume sequence complete (parallel wave)" >> RESUME_20261103.log
echo "[$(date -u +%H:%M:%SZ)] wave3 complete (parallel wave)" >> WAVE3_20261103.log
say "PARALLEL WAVE COMPLETE"
