#!/usr/bin/env python3
"""POST-FREEZE AUTH_SMOKE (Amendment 3) — 16-token health probe per label.

NON-EVIDENCE, logged inside this namespace only.  This script is deliberately
NOT run before the namespace-restricted freeze commit and the user's explicit
authorization; it is included in the freeze bundle so the exact probe code is
frozen alongside the runner.  It goes through the EXACT ApinexClient used by
the runner; the key is read from APINEX_API_KEY and never written to any
artifact.

Run only after the freeze commit:
    APINEX_API_KEY=... python3 smoke_auth_amend3.py
"""

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apinex_client import ApinexClient, ProviderFailure  # noqa: E402

LABELS = ["free/gpt-6-luna", "free/qwen-3.8-max", "free/deepseek-v4.1-flash"]


def main() -> int:
    key = os.environ.get("APINEX_API_KEY", "").strip()
    if not key:
        sys.exit("APINEX_API_KEY is not set in the process environment")
    probes, cost = [], 0.0
    for label in LABELS:
        client = ApinexClient(key, label)
        probe = {"model": label, "probe": "POST /v1/chat/completions (16-token smoke)",
                 "attempted": time.time()}
        try:
            result = client.call("Reply with exactly: OK", 16)
            usage = result["metadata"].get("usage") or {}
            probe["result"] = "ok"
            probe["observed"] = {
                "reply": result["text"][:40],
                "finish_reason": result["metadata"].get("finish_reason"),
                "usage": usage,
                "cost_tokens": usage.get("cost_tokens"),
            }
            cost += 0.0
        except ProviderFailure as exc:
            probe["result"] = "PROVIDER_FAILURE"
            probe["observed"] = {"category": exc.category,
                                 "http_status": exc.http_status}
        probes.append(probe)

    health = {
        "namespace": "external_admission_amend3_20261105",
        "recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "classification": "AUTH_SMOKE, non-evidence",
        "purpose": ("Provider health verification before Amendment-3 sessions; "
                    "excluded from all analyses per project protocol"),
        "config": {
            "route": "APINEX OpenAI-compatible /v1/chat/completions",
            "endpoint": "https://api.apinex.bond/v1/chat/completions",
            "labels": LABELS,
            "identity_note": ("provider-attested labels only; no hosted-weight "
                              "identity claimed"),
            "key_handling": ("APINEX_API_KEY read from the process environment "
                             "at runtime; never printed, never written to any "
                             "sp2027 artifact"),
        },
        "probes": probes,
        "estimated_cost_usd": cost,
    }
    (HERE / "HEALTH.json").write_text(json.dumps(health, indent=2, sort_keys=True) + "\n")
    ledger = Path("/mnt/nvme5/ACTS-Attack/sp2027/research_execution/BUDGET_LEDGER.jsonl")
    with ledger.open("a") as f:
        for probe in probes:
            f.write(json.dumps({
                "timestamp": time.strftime("%Y-%m-%d"),
                "namespace": "external_admission_amend3_20261105",
                "call_class": "AUTH_SMOKE non-evidence",
                "calls": 1,
                "model": probe["model"],
                "input_tokens": (probe.get("observed", {}).get("usage") or {}).get("prompt_tokens", 0),
                "output_tokens": (probe.get("observed", {}).get("usage") or {}).get("completion_tokens", 0),
                "estimated_accounting_cost_usd": 0.0,
                "invoice_status": "free tier; cost_tokens 0",
                "source": "external_admission_amend3_20261105/HEALTH.json",
            }, sort_keys=True) + "\n")
    print(json.dumps({"classification": health["classification"],
                      "labels": LABELS,
                      "results": {p["model"]: p["result"] for p in probes},
                      "estimated_cost_usd": cost}, indent=2))
    return 0 if all(p["result"] == "ok" for p in probes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
