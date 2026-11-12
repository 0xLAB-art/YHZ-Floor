#!/usr/bin/env python3
"""Append one cohort's per-call rows to BUDGET_LEDGER.jsonl.

Usage: append_budget_to_ledger.py <namespace-dir> [--dry-run]

Token counts come from the cohort's stored raw provider responses
(`usage.input_tokens` / `usage.output_tokens`), not from estimates. Cost uses the
same accounting basis as every prior ledger entry (USD 3/M in + USD 15/M out),
stated in `pricing_basis`, because router routes return no invoice.

Idempotent on (run_id, turn): safe to run while a cohort is live and again at
finalization. Sessions with no stored response (terminal provider failures) get
no row — they cost nothing and are counted in the cohort's own results file.
"""
import json
import sys
import time
from pathlib import Path

IN_USD_PER_M, OUT_USD_PER_M = 3.0, 15.0
LEDGER = Path(__file__).resolve().parent / "BUDGET_LEDGER.jsonl"


def main(argv):
    if len(argv) < 2:
        raise SystemExit("usage: append_budget_to_ledger.py <namespace-dir> [--dry-run]")
    ns = Path(argv[1]).resolve()
    dry = "--dry-run" in argv
    results = ns / "results.jsonl"
    if not results.exists():
        raise SystemExit(f"no results.jsonl in {ns}")

    existing = set()
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if "run_id" in r:
                    existing.add((r.get("run_id"), r.get("turn")))

    rows = []
    for line in results.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        run_id = rec["run_id"]
        for path in sorted((ns / "raw_provider_responses").glob(run_id + "__turn*.json")):
            turn = int(path.stem.split("__turn")[-1])
            if (run_id, turn) in existing:
                continue
            body = json.loads(path.read_text())
            usage = body.get("usage") or {}
            tin = int(usage.get("input_tokens") or 0)
            tout = int(usage.get("output_tokens") or 0)
            rows.append({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(path.stat().st_mtime)),
                "namespace": ns.name, "protocol": rec.get("protocol"),
                "run_id": run_id, "seed": rec.get("seed"), "cell": rec.get("cell"),
                "turn": turn, "call_type": "experiment", "model": body.get("model"),
                "input_tokens": tin, "output_tokens": tout,
                "estimated_accounting_cost_usd": round(
                    tin / 1e6 * IN_USD_PER_M + tout / 1e6 * OUT_USD_PER_M, 6),
                "pricing_basis": "USD 3/M input + USD 15/M output (same accounting basis as prior ledger entries)",
                "invoice_status": "not claimed; router route, no invoice",
                "cumulative_authorized_alert_usd": 50, "cumulative_hard_stop_usd": 200,
            })

    if not dry:
        with LEDGER.open("a") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")

    total = sum(r["estimated_accounting_cost_usd"] for r in rows)
    print(f"{'would append' if dry else 'appended'} {len(rows)} rows for {ns.name} "
          f"| cost this run ${total:.6f}")


if __name__ == "__main__":
    main(sys.argv)
