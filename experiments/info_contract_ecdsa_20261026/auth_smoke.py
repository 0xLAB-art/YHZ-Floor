"""AUTH_SMOKE provider health probe for P012-INFO-CONTRACT-2X2-ECDSA-NONCE-REUSE-v1.

Step zero: exactly ONE 16-token generation probe through the EXACT provider
code path the session runner uses (provider_adapter.ClaudeProvider — the same
import the P012 module performs), BEFORE any experiment session. Logged as
AUTH_SMOKE, non-evidence. Appends one BUDGET_LEDGER.jsonl line labeled
non-evidence.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parents[1] / "analysis/checkpoint007_active_experiments/runs_009"
sys.path.insert(0, str(RUNS))

from provider_adapter import ClaudeProvider, ProviderFailure  # noqa: E402

LEDGER = HERE.parents[0] / "BUDGET_LEDGER.jsonl"
PROTOCOL = "P012-INFO-CONTRACT-2X2-ECDSA-NONCE-REUSE-v1"


def main():
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    started = time.time()
    provider = ClaudeProvider()
    record = {
        "protocol": PROTOCOL,
        "namespace": HERE.name,
        "kind": "AUTH_SMOKE",
        "evidence": False,
        "probe": "Reply with the single word OK.",
        "max_tokens": 16,
        "timestamp": started,
        "route": {"endpoint": provider.endpoint, "model": provider.model},
    }
    ok = False
    usage = {}
    try:
        r = provider.call(record["probe"], 16)
        meta = dict(r["metadata"])
        usage = meta.get("usage", {}) or {}
        (HERE / "auth_smoke_raw.json").write_text(r["raw_body"])
        record.update({
            "result": "OK",
            "finish_reason": meta.get("finish_reason"),
            "usage": usage,
            "attest": provider.attest(),
            "wall_s": round(time.time() - started, 3),
        })
        ok = True
    except ProviderFailure as exc:
        record.update({"result": "FAILED", "category": exc.category,
                       "message": str(exc), "wall_s": round(time.time() - started, 3)})
    (HERE / "HEALTH.json").write_text(json.dumps(record, indent=2, sort_keys=True, default=str) + "\n")
    in_toks = int(usage.get("input_tokens") or 0)
    out_toks = int(usage.get("output_tokens") or 0)
    with LEDGER.open("a") as f:
        f.write(json.dumps({
            "timestamp": ts,
            "protocol": PROTOCOL,
            "namespace": HERE.name,
            "call_type": "AUTH_SMOKE",
            "non_evidence": True,
            "calls": 1,
            "input_tokens": in_toks,
            "output_tokens": out_toks,
            "estimated_accounting_cost_usd": round((in_toks * 3 + out_toks * 15) / 1e6, 6),
            "pricing_basis": "claude-sonnet list USD 3/M input + USD 15/M output (same basis as prior ledger entries)",
            "invoice_status": "provider-reported free route; no invoice claimed",
            "status": "health probe ok" if ok else "health probe FAILED",
            "source": HERE.name + "/auth_smoke.py",
        }, sort_keys=True) + "\n")
    print(json.dumps({"ok": ok, "category": record.get("category"),
                      "usage": usage, "log": "HEALTH.json"}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
