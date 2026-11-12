#!/usr/bin/env python3
"""Pre-freeze provider-route probe — Amendment 3 (NON-EVIDENCE).

16-token health checks through the exact ApinexClient used by the runner.
No task prompt, no task content; recorded only to document route availability
and free-tier accounting.  The key is read from APINEX_API_KEY and is never
written to the record.

Run: APINEX_API_KEY=... python3 probe_apinex_route.py
"""

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "HEALTH_ROUTE_PROBE.json"
sys.path.insert(0, str(HERE))
from apinex_client import ApinexClient, ProviderFailure  # noqa: E402

PROBE_MODELS = [
    "free/gpt-6-luna",
    "free/qwen-3.8-max",
    "free/deepseek-v4.1-flash",
    "free/kimi-k3",
]
SELECTED = PROBE_MODELS[:3]


def main():
    key = os.environ.get("APINEX_API_KEY", "").strip()
    if not key:
        raise SystemExit("APINEX_API_KEY is not set")
    probes = []
    for model in PROBE_MODELS:
        client = ApinexClient(key, model)
        started = time.time()
        try:
            result = client.call("Reply with exactly: OK", 16)
            usage = result["metadata"].get("usage") or {}
            probes.append({
                "model": model,
                "status": "ok",
                "reply": result["text"][:40],
                "finish_reason": result["metadata"].get("finish_reason"),
                "usage": usage,
                "cost_tokens": usage.get("cost_tokens"),
                "latency_s": round(time.time() - started, 3),
            })
        except ProviderFailure as exc:
            probes.append({
                "model": model,
                "status": "FAIL",
                "category": exc.category,
                "http_status": exc.http_status,
                "detail": str(exc)[:200],
                "latency_s": round(time.time() - started, 3),
            })
    payload = {
        "schema": "external-admission-amend3-route-probe/1",
        "classification": "ROUTE_PROBE, non-evidence",
        "recorded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "purpose": ("pre-freeze provider-route selection and free-tier health; "
                    "no task prompt or task content; excluded from all analyses"),
        "provider": {
            "route": "APINEX OpenAI-compatible /v1/chat/completions",
            "endpoint": "https://api.apinex.bond/v1/chat/completions",
            "key_handling": ("APINEX_API_KEY read from the process environment "
                             "at runtime; never printed, never written to any "
                             "sp2027 artifact"),
            "tier": "free (usage cost_tokens 0; no invoice claim)",
        },
        "probe": {"max_tokens": 16, "temperature": 0.2,
                  "prompt": "Reply with exactly: OK"},
        "probes": probes,
        "selected_labels": SELECTED,
        "previous_route_note": ("the earlier single-route plan (claude-sonnet-"
                                "4-6-free via APMIX) was found unavailable "
                                "pre-freeze: APMIX 404; agentrouter keys 401. "
                                "No task-prompt call was made on it."),
        "boundary": ("Route availability record only; not experiment evidence, "
                     "not a benchmark-quality claim."),
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"selected": SELECTED,
                      "statuses": {p["model"]: p["status"] for p in probes},
                      "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
