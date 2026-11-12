#!/usr/bin/env python3
"""Gateway probe for external_published_audit_20261110 (NON-EVIDENCE).
Lists served models + 16-token smoke on targets. Key from env, never logged."""
import json, os, sys, urllib.request, time

BASE = "https://api.apinex.bond"
key = os.environ.get("APINEX_API_KEY", "").strip()
if not key:
    sys.exit("APINEX_API_KEY not set")

def req(path, payload=None):
    r = urllib.request.Request(BASE + path, method="POST" if payload else "GET",
        data=json.dumps(payload).encode() if payload else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]

code, models = req("/v1/models")
print(f"GET /v1/models -> {code}")
if code == 200:
    ids = sorted(m.get("id", "") for m in models.get("data", []))
    print(f"served models: {len(ids)}")
    for pat in ("gpt-4o", "gpt-4", "gpt-6.1", "gpt-5.6", "6.1-sol", "claude", "free/"):
        hits = [i for i in ids if pat in i.lower()][:6]
        print(f"  [{pat}] -> {hits}")
else:
    print(models)

for label in [m for m in ["gpt-4o", "gpt-4o-2024-11-20", "gpt-6.1-sol"] if any(m in str(x) for x in models.get("data", []))] if code == 200 else []:
    code2, out = req("/v1/chat/completions", {"model": label, "max_tokens": 16,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}]})
    ok = code2 == 200
    print(f"smoke {label}: {code2} {'OK' if ok else str(out)[:120]} time={time.strftime('%H:%M:%S')}")
