#!/usr/bin/env python3
"""APMix entitlement sweep (2026-11-02).

403 "needs the <X> plan" on gpt-6-astra and gemini-3.1-pro shows the key is
valid but tier-limited, so SOME ids are reachable. This sweeps a bounded list of
candidate ids (max_tokens=16, off-fixture prompt) and records, per id:
entitled (OK with text), gated (403, plan name extracted), or unknown (404).
No fixture, no cell slot; nothing here counts as a session.
"""
import json, os, re, time
from pathlib import Path
import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
SMOKE = "Reply with exactly one word: READY"
CANDS = ["claude-sonnet-5.5", "claude-fable-5.1", "claude-opus-4.6", "gpt-6-luna",
         "gpt-6.1-terra", "glm-5.3", "glm-5.3-flash", "deepseek-v4-pro",
         "deepseek-v4-flash", "kimi-k3.1-pro", "qwen-3.8-max", "grok-4.7",
         "minimax-m3", "mimo-v2.6-pro", "hy4-preview"]

def load_env():
    for line in (ROOT / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()
key = os.environ.get("APMIX_API_KEY", "").strip()
out = {"probe": "apmix-entitlement-20261102", "started": time.time(),
       "candidates": [], "entitled": [], "prompt": SMOKE}
for mid in CANDS:
    t0 = time.time()
    rec = {"model": mid}
    try:
        r = requests.post("https://api.apmix.ai/v1/messages",
            headers={"x-api-key": key, "Authorization": "Bearer " + key,
                     "anthropic-version": "2023-06-01", "content-type": "application/json",
                     "User-Agent": UA},
            json={"model": mid, "max_tokens": 16, "messages": [{"role": "user", "content": SMOKE}]},
            timeout=60, allow_redirects=False)
    except requests.RequestException as exc:
        rec.update(status="UNREACHABLE", error=type(exc).__name__)
        out["candidates"].append(rec); print(json.dumps(rec)); continue
    try: body = r.json()
    except ValueError: body = {}
    err = body.get("error") if isinstance(body.get("error"), dict) else {}
    msg = str(err.get("message", ""))
    text = "".join(c.get("text", "") for c in (body.get("content") or []) if isinstance(c, dict))
    plan = (re.search(r"needs the ([A-Za-z0-9 ]+) plan", msg) or [None, None])[1]
    rec.update(http_status=r.status_code, latency_s=round(time.time() - t0, 1))
    if r.ok and text.strip():
        rec.update(status="ENTITLED", output_head=text.strip()[:40])
        out["entitled"].append(mid)
    elif r.ok:
        rec.update(status="OK_EMPTY")
    elif r.status_code == 403:
        rec.update(status="GATED", plan_required=plan)
    elif r.status_code == 404:
        rec.update(status="UNKNOWN_MODEL")
    else:
        rec.update(status="HTTP_ERROR", error_message=msg[:120])
    out["candidates"].append(rec)
    print(json.dumps(rec)[:200])

out["finished"] = time.time()
(HERE / "apmix_entitlement_20261102.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print("\nENTITLED:", out["entitled"])
