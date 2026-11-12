#!/usr/bin/env python3
"""AUTH_SMOKE provider health probe for Phase 1 (H2: CBC agency/delegation).

Step zero of the phase: one 16-token probe, logged as AUTH_SMOKE non-evidence.
Protocol of the 2026-10-18 NO-GO pilot: health must be verified BEFORE session
creation. The API key is read from the root .env and is NEVER printed, logged,
or written to any file under sp2027/.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

NS = Path(__file__).resolve().parent           # .../h2_cbc_agency_20261023/provider_health
REPO_ROOT = NS.parents[3]                      # /mnt/nvme5/ACTS-Attack
OUT = NS / "AUTH_SMOKE.json"
ENV_PATH = REPO_ROOT / ".env"


def load_env(path):
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main():
    env = load_env(ENV_PATH)
    base = env.get("APMIX_BASE_URL", "").rstrip("/")
    model = env.get("APMIX_MODEL", "")
    key = env.get("APMIX_API_KEY", "")
    endpoint = (base + "/messages") if base.endswith("/v1") else (base + "/v1/messages")
    if not (base and model and key):
        print(json.dumps({"result": "CONFIG_MISSING",
                          "have": {"base": bool(base), "model": bool(model), "key": bool(key)}}))
        return 2
    payload = {"model": model, "max_tokens": 16,
               "messages": [{"role": "user", "content": "Reply with exactly: OK"}]}
    headers = {"x-api-key": key, "Authorization": "Bearer " + key,
               "anthropic-version": "2023-06-01", "content-type": "application/json"}
    started = time.time()
    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=120)
    except requests.RequestException as exc:
        OUT.write_text(json.dumps({
            "classification": "AUTH_SMOKE, non-evidence",
            "phase": "Phase 1 H2 CBC agency/delegation",
            "endpoint": endpoint, "model_requested": model,
            "result": "PROVIDER_UNAVAILABLE",
            "error_category": type(exc).__name__,
            "recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }, indent=2) + "\n")
        print(json.dumps({"result": "PROVIDER_UNAVAILABLE", "error": type(exc).__name__}))
        return 1
    body = {}
    try:
        body = r.json()
    except ValueError:
        pass
    text = "".join(x.get("text", "") for x in (body.get("content") or [])
                   if isinstance(x, dict) and x.get("type") == "text")
    ok = r.status_code < 400 and bool(text)
    record = {
        "classification": "AUTH_SMOKE, non-evidence",
        "phase": "Phase 1 H2 CBC agency/delegation",
        "purpose": "provider health verification before session creation; excluded from all analyses",
        "endpoint": endpoint,
        "model_requested": model,
        "model_provider_attested": body.get("model"),
        "http_status": r.status_code,
        "stop_reason": body.get("stop_reason"),
        "provider_response_id": body.get("id"),
        "reply_text": text[:64],
        "usage": body.get("usage", {}),
        "latency_seconds": round(time.time() - started, 3),
        "max_tokens": 16,
        "key_handling": "key read from root .env at runtime; never logged; response headers not retained",
        "result": "ok" if ok else "FAILED",
        "recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": record["result"], "http_status": r.status_code,
                      "stop_reason": body.get("stop_reason"), "usage": body.get("usage", {}),
                      "model_attested": body.get("model")}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
