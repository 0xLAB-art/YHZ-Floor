#!/bin/bash
# Registered resume driver: relaunches the frozen runner on each registered
# halt until 168 sessions or 20 cycles. Each cycle is an append-only run_log
# entry; blocked slots record terminal PROVIDER_UNAVAILABLE rows and are
# skipped by the resume logic (rows never deleted).
cd /mnt/nvme5/ACTS-Attack/sp2027/research_execution/external_admission_amend4_frontier_20261106
for i in $(seq 1 20); do
  N=$(wc -l < results.jsonl 2>/dev/null || echo 0)
  if [ "$N" -ge 168 ]; then echo "COMPLETE at cycle $i"; break; fi
  echo "=== resume cycle $i (sessions: $N) ===" >> run_log.txt
  AGENTROUTER_API_KEY=sk-CYh3bW3LO3Vq4NEIRVB5q0Gkrogzl2zsKhPfJfffyyuRtKZA python3 -I run_amend4_sessions.py >> run_log.txt 2>&1
  sleep 15
done
echo "driver finished: $(wc -l < results.jsonl) sessions"
