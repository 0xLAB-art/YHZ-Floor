"""SMOKE provider health probe for P010L4-INFO-CONTRACT-2X2-CHACHA20-KIMIK3-v1.

Step zero: exactly ONE 16-token generation probe through the EXACT provider
code path the session runner uses (provider_adapter.ClaudeProvider with the
Ollama-gateway environment the wrapper sets), BEFORE the freeze commit.
Logged as SMOKE, non-evidence. Appends one BUDGET_LEDGER.jsonl line labeled
non-evidence.
"""
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parents[1] / "analysis/checkpoint007_active_experiments/runs_009"
sys.path.insert(0, str(RUNS))

# Same configuration-only redirect the wrapper applies.
os.environ["ACTS_PROVIDER_ENDPOINT"] = "http://127.0.0.1:11434/v1"
os.environ["ACTS_PROVIDER_MODEL"] = "kimi-k3:cloud"
os.environ.pop("ACTS_PROVIDER_API_KEY", None)

from provider_adapter import ClaudeProvider, ProviderFailure  # noqa: E402

LEDGER = HERE.parents[1] / "BUDGET_LEDGER.jsonl"
PROTOCOL = "P010L4-INFO-CONTRACT-2X2-CHACHA20-KIMIK3-v1"


def main():
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    started = time.time()
    provider = ClaudeProvider()
    record = {
        "protocol": PROTOCOL,
        "namespace": HERE.name,
        "kind": "SMOKE",
        "evidence": False,
        "probe": "Reply with the single word OK.",
        "max_tokens": 16,
        "model": os.environ.get("ACTS_PROVIDER_MODEL"),
        "endpoint": os.environ.get("ACTS_PROVIDER_ENDPOINT"),
    }
    try:
        resp = provider.call(record["probe"], record["max_tokens"])
        text = getattr(resp, "text", None) or (resp.get("text") if isinstance(resp, dict) else "")
        record.update({
            "http": 200,
            "stop_reason": getattr(resp, "stop_reason", None)
            or (resp.get("stop_reason") if isinstance(resp, dict) else None),
            "text_head": str(text)[:40],
            "latency_s": round(time.time() - started, 2),
            "status": "OK",
        })
    except ProviderFailure as e:
        record.update({"status": "PROVIDER_FAILURE", "detail": str(e)[:200]})
    except Exception as e:  # noqa: BLE001
        record.update({"status": "ERROR", "detail": str(e)[:200]})

    (HERE / "SMOKE.json").write_text(json.dumps(record, indent=1) + "\n")
    with LEDGER.open("a") as f:
        f.write(json.dumps({
            "date": ts, "namespace": HERE.name, "role": "auth_smoke_non_evidence",
            "protocol": PROTOCOL, "model": record["model"],
            "status": record["status"],
        }) + "\n")
    print(json.dumps(record, indent=1))


if __name__ == "__main__":
    main()
