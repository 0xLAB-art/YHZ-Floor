#!/usr/bin/env python3
"""Append P014 per-call rows to BUDGET_LEDGER.jsonl (prereg §3 commitment).

Token counts come from the stored raw provider responses (usage.input_tokens /
usage.output_tokens, summed over turns of a session). Cost uses the SAME
accounting basis as every prior ledger entry (USD 3/M input + USD 15/M output),
stated in `pricing_basis`, because the route returns no invoice.

Idempotent: a (run_id, turn) already present is never appended twice, so this can
run during the cohort and again at finalization.
"""
import json, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE / "info_contract_aesgcm_20261102"
LEDGER = HERE / "BUDGET_LEDGER.jsonl"
RAW = NS / "raw_provider_responses"
IN_USD_PER_M, OUT_USD_PER_M = 3.0, 15.0

existing = set()
if LEDGER.exists():
    for line in LEDGER.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if "run_id" in r:
                existing.add((r.get("run_id"), r.get("turn")))

rows = []
for line in (NS / "results.jsonl").read_text().splitlines():
    if not line.strip():
        continue
    rec = json.loads(line)
    run_id = rec["run_id"]
    turns = sorted(RAW.glob(run_id + "__turn*.json"))
    if not turns:
        continue  # provider-failure session: no response, no token accounting
    for path in turns:
        turn = int(path.stem.split("__turn")[-1])
        if (run_id, turn) in existing:
            continue
        body = json.loads(path.read_text())
        usage = body.get("usage") or {}
        tin = int(usage.get("input_tokens") or 0)
        tout = int(usage.get("output_tokens") or 0)
        cost = round(tin / 1e6 * IN_USD_PER_M + tout / 1e6 * OUT_USD_PER_M, 6)
        rows.append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(path.stat().st_mtime)),
            "namespace": NS.name, "protocol": rec["protocol"],
            "run_id": run_id, "seed": rec["seed"], "cell": rec["cell"], "turn": turn,
            "call_type": "experiment", "model": body.get("model"),
            "input_tokens": tin, "output_tokens": tout,
            "estimated_accounting_cost_usd": cost,
            "pricing_basis": "USD 3/M input + USD 15/M output (same accounting basis as prior ledger entries)",
            "invoice_status": "not claimed; router route, no invoice",
            "cumulative_authorized_alert_usd": 50, "cumulative_hard_stop_usd": 200,
        })

with LEDGER.open("a") as fh:
    for r in rows:
        fh.write(json.dumps(r, sort_keys=True) + "\n")

total = sum(r["estimated_accounting_cost_usd"] for r in rows)
print(f"appended {len(rows)} rows | cohort cost this run ${total:.6f}")
allrows = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
mine = [r for r in allrows if r.get("namespace") == NS.name]
print(f"ledger cohort rows now {len(mine)} | cumulative ${sum(r['estimated_accounting_cost_usd'] for r in mine):.6f}")
