#!/usr/bin/env python3
"""Step zero (amendment 1): one 16-token AUTH_SMOKE provider health probe.

Non-evidence, logged inside this namespace only. The probe goes through the
EXACT session code path: the frozen ApmixClient of the basis namespace
(external_admission_20261024/apmix_client.py), whose SHA-256 is asserted at
import time against the basis FREEZE.json value, so the probe and the later
experiment sessions provably use the same frozen client.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASIS = HERE.parent / "external_admission_20261024"
BASIS_CLIENT_SHA256 = "e6a3ae330640cf61a81268b478abe421c8e0137968e337994ad443ba6c12fb46"

got = hashlib.sha256((BASIS / "apmix_client.py").read_bytes()).hexdigest()
if got != BASIS_CLIENT_SHA256:
    sys.exit(f"FROZEN CLIENT HASH MISMATCH: {got}")
sys.path.insert(0, str(BASIS))
from apmix_client import ApmixClient, ProviderFailure  # noqa: E402

OUT = HERE


def main() -> int:
    client = ApmixClient()
    probe = {"probe": "POST /v1/messages (16-token smoke)", "attempted": time.time()}
    try:
        result = client.call("Reply with exactly: OK", 16)
        body = json.loads(result["raw_body"])
        probe["result"] = "ok"
        probe["observed"] = {
            "id": body.get("id"), "stop_reason": body.get("stop_reason"),
            "model_label": body.get("model"), "reply": result["text"][:80],
            "usage": body.get("usage", {}),
        }
        cost_usd = (body.get("usage", {}).get("input_tokens", 0) * 3e-6
                    + body.get("usage", {}).get("output_tokens", 0) * 15e-6)
    except ProviderFailure as exc:
        probe["result"] = "PROVIDER_FAILURE"
        probe["observed"] = {"category": exc.category, "http_status": exc.http_status}
        cost_usd = 0.0
    health = {
        "namespace": "external_admission_amend1_20261024",
        "recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "classification": "AUTH_SMOKE, non-evidence",
        "purpose": ("Provider health verification before Amendment-1 sessions; "
                    "excluded from all analyses per project protocol (2026-10-18 NO-GO pilot)"),
        "config": {"base_url": client.endpoint, "model": client.model,
                   "identity_note": "provider-attested route label only; no hosted-weight identity claimed",
                   "client_code_path": "external_admission_20261024/apmix_client.py (frozen, hash-asserted)"},
        "probes": [probe],
        "precedent": "2026-10-18 contract-sound pilot invalidated by pre-output HTTP 401s; health must be verified before session creation",
        "estimated_cost_usd": cost_usd,
    }
    (OUT / "HEALTH.json").write_text(json.dumps(health, indent=2, sort_keys=True) + "\n")
    ledger_line = {
        "timestamp": time.strftime("%Y-%m-%d"),
        "namespace": "external_admission_amend1_20261024",
        "call_class": "AUTH_SMOKE non-evidence",
        "calls": 1,
        "input_tokens": probe.get("observed", {}).get("usage", {}).get("input_tokens", 0),
        "output_tokens": probe.get("observed", {}).get("usage", {}).get("output_tokens", 0),
        "estimated_accounting_cost_usd": round(cost_usd, 9),
        "invoice_status": "not claimed; provider route reported free plan",
        "source": "external_admission_amend1_20261024/HEALTH.json",
    }
    ledger = Path("/mnt/nvme5/ACTS-Attack/sp2027/research_execution/BUDGET_LEDGER.jsonl")
    with ledger.open("a") as f:
        f.write(json.dumps(ledger_line, sort_keys=True) + "\n")
    print(json.dumps({k: health[k] for k in ("classification", "probes", "estimated_cost_usd")}, indent=2))
    return 0 if probe["result"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
