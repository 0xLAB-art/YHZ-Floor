#!/usr/bin/env python3
"""AUTH_SMOKE provider health probe for H2-CBC-PAIRS-EXT-20261024-v1.

Step zero of the phase: ONE 16-token probe through the EXACT session code
path — it imports ProviderClient from this namespace's runner (the verbatim
post-A2 client of the frozen cohort plus this phase's recorded guards) and
calls provider.call() exactly as a session turn does. Protocol of the
2026-10-18 NO-GO pilot: health must be verified BEFORE session creation.
Classification: AUTH_SMOKE, non-evidence; excluded from all analyses.
The API key is read from the operator-owned root .env inside
ProviderClient and is NEVER printed, logged, or written to any file under
sp2027/.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent           # .../provider_health
NS = HERE.parent                                  # .../h2_pairs_extension_20261024
sys.path.insert(0, str(NS))
from run_h2_pairs_extension import ProviderClient, PROTOCOL  # noqa: E402

OUT = HERE / "AUTH_SMOKE.json"
LEDGER = NS.parent / "BUDGET_LEDGER.jsonl"
RATE_INPUT_PER_MTOK = 3.0
RATE_OUTPUT_PER_MTOK = 15.0


def main():
    started = time.time()
    try:
        provider = ProviderClient()
    except Exception as exc:  # noqa: BLE001 — config/SSRF-guard failures are infra, recorded verbatim
        OUT.write_text(json.dumps({
            "classification": "AUTH_SMOKE, non-evidence",
            "protocol": PROTOCOL,
            "result": "PROVIDER_UNAVAILABLE",
            "stage": "provider_client_init",
            "error_category": type(exc).__name__,
            "detail": str(exc)[:300],
            "recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"result": "PROVIDER_UNAVAILABLE", "stage": "provider_client_init",
                          "error": type(exc).__name__}))
        return 1
    try:
        result = provider.call("Reply with exactly: OK", 16)
    except Exception as exc:  # noqa: BLE001 — ProviderFailure or guard, recorded verbatim
        OUT.write_text(json.dumps({
            "classification": "AUTH_SMOKE, non-evidence",
            "protocol": PROTOCOL,
            "result": "PROVIDER_UNAVAILABLE",
            "stage": "provider_call",
            "error_category": getattr(exc, "category", type(exc).__name__),
            "detail": str(exc)[:300],
            "recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"result": "PROVIDER_UNAVAILABLE", "stage": "provider_call",
                          "error": getattr(exc, "category", type(exc).__name__)}))
        return 1
    meta = result["metadata"]
    usage = meta["usage"] or {}
    in_tok = int(usage.get("input_tokens", 0))
    out_tok = int(usage.get("output_tokens", 0))
    record = {
        "classification": "AUTH_SMOKE, non-evidence",
        "protocol": PROTOCOL,
        "purpose": ("provider health verification before session creation, through the "
                    "exact ProviderClient.call session code path; excluded from all analyses"),
        "endpoint": meta["endpoint"],
        "model_requested": meta["model_requested"],
        "model_provider_attested": meta["provider_model"],
        "http_status": meta["http_status"],
        "stop_reason": meta["finish_reason"],
        "reply_text": result["text"][:64],
        "usage": usage,
        "latency_seconds": round(time.time() - started, 3),
        "max_tokens": 16,
        "key_handling": "key read from root .env inside ProviderClient; never logged; response headers not retained",
        "result": "ok" if (meta["http_status"] == 200 and bool(result["text"])
                           and meta["finish_reason"] not in ("max_tokens", "length")) else "FAILED",
        "recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    with LEDGER.open("a") as f:
        f.write(json.dumps({
            "timestamp": time.strftime("%Y-%m-%d", time.gmtime()),
            "namespace": PROTOCOL, "classification": "auth_smoke_non_evidence",
            "protocol": PROTOCOL, "run_id": "AUTH_SMOKE", "arm": None, "seed": None,
            "turn": None, "call_index": "auth_smoke", "model": meta["model_requested"],
            "input_tokens": in_tok, "output_tokens": out_tok,
            "estimated_accounting_cost_usd": round(
                in_tok * RATE_INPUT_PER_MTOK / 1e6 + out_tok * RATE_OUTPUT_PER_MTOK / 1e6, 9),
            "invoice_status": "not claimed; provider route reported free plan",
        }, sort_keys=True) + "\n")
    print(json.dumps({"result": record["result"], "http_status": meta["http_status"],
                      "stop_reason": meta["finish_reason"], "usage": usage,
                      "model_attested": meta["provider_model"],
                      "code_path": "ProviderClient.call (exact session path)"}))
    return 0 if record["result"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
