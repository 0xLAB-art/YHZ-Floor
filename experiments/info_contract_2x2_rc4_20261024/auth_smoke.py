"""AUTH_SMOKE provider health probe for P011-INFO-CONTRACT-2X2-RC4-v1.

Step zero of the phase: exactly ONE 16-token generation probe through the
exact provider code path used by the session runner, BEFORE any experiment
session and BEFORE the preregistration freeze commit is consumed by sessions.
Logged inside the namespace as AUTH_SMOKE, non-evidence (protocol of the
2026-10-18 NO-GO pilot: health must be verified before session creation).
Appends one BUDGET_LEDGER.jsonl line labeled non-evidence.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from provider_client import ClaudeProvider, ProviderFailure  # noqa: E402

OUT = HERE / "preflight"
OUT.mkdir(parents=True, exist_ok=True)
LEDGER = HERE.parents[0] / "BUDGET_LEDGER.jsonl"
PROTOCOL = "P011-INFO-CONTRACT-2X2-RC4-v1"


def ledger_append(record):
    with LEDGER.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def main():
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    provider = ClaudeProvider()
    record = {
        "protocol": PROTOCOL,
        "classification": "AUTH_SMOKE, non-evidence",
        "probe": "Reply with the single word OK.",
        "max_tokens": 16,
        "utc": ts,
        "model_route": provider.model,
        "endpoint": provider.messages_url,
    }
    ok = False
    usage = {}
    try:
        r = provider.call(record["probe"], 16)
        meta = dict(r["metadata"])
        usage = meta.get("usage", {}) or {}
        raw_name = f"auth_smoke_raw_{ts}.json"
        (OUT / raw_name).write_text(r["raw_body"])
        record.update({
            "ok": True,
            "provider_metadata": meta,
            "text_head": r["text"][:120],
            "raw_body_path": str(OUT / raw_name),
        })
        ok = True
    except ProviderFailure as exc:
        record.update({"ok": False, "category": exc.category, "message": str(exc)})
    (OUT / f"auth_smoke_{ts}.json").write_text(json.dumps(record, indent=2, sort_keys=True, default=str) + "\n")
    in_toks = int(usage.get("input_tokens") or 0)
    out_toks = int(usage.get("output_tokens") or 0)
    ledger_append({
        "timestamp": ts,
        "phase": "Phase 3",
        "protocol": PROTOCOL,
        "namespace": HERE.name,
        "call_type": "AUTH_SMOKE",
        "non_evidence": True,
        "calls": 1,
        "input_tokens": in_toks,
        "output_tokens": out_toks,
        "estimated_accounting_cost_usd": round((in_toks * 3 + out_toks * 15) / 1e6, 6),
        "pricing_basis": "claude-sonnet list USD 3/M input + USD 15/M output (same basis as prior ledger entries)",
        "cumulative_authorized_alert_usd": 50,
        "cumulative_hard_stop_usd": 200,
        "status": "health probe ok" if ok else "health probe FAILED",
        "source": "info_contract_2x2_rc4_20261024/auth_smoke.py",
    })
    print(json.dumps({"ok": ok, "category": record.get("category"),
                      "usage": usage, "log": f"preflight/auth_smoke_{ts}.json"}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
