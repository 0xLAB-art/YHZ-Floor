#!/usr/bin/env python3
"""Second, narrower reachability probe (2026-11-02).

Follow-ups indicated by route_probe_20261102.json:
  - OpenRouter answered GET /models (public) but every smoke call returned 401
    "Missing Authentication header" while Authorization was set -> check whether
    the loaded key is non-empty and retry with Authorization ONLY (no x-api-key).
  - APMix 404 said its API is served from https://api.apmix.ai/v1 and the
    configured APMIX_MODEL is unknown -> retry at that base with a few ids taken
    from the APINEX catalog (same router ecosystem naming).
Still no fixture, no cell slot: 16-token smoke calls only. Keys never printed.
"""
import json, os, time
from pathlib import Path
import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
SMOKE = "Reply with exactly one word: READY"

def load_env():
    p = ROOT / ".env"
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()
out = {"probe": "route-probe2-20261102", "started": time.time(), "checks": []}

def post(url, headers, payload, label, shape="openai"):
    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=90, allow_redirects=False)
    except requests.RequestException as exc:
        rec = {"label": label, "url": url, "status": "UNREACHABLE", "error": type(exc).__name__}
        out["checks"].append(rec); print(json.dumps(rec)); return rec
    try: body = r.json()
    except ValueError: body = {}
    if shape == "openai":
        text = ""
        for ch in (body.get("choices") or []):
            text = ((ch.get("message") or {}).get("content") or ""); break
    else:
        text = "".join(c.get("text", "") for c in (body.get("content") or []) if isinstance(c, dict))
    rec = {"label": label, "url": url, "http_status": r.status_code,
           "latency_s": round(time.time() - t0, 1),
           "status": "OK" if (r.ok and text.strip()) else ("OK_EMPTY" if r.ok else "HTTP_ERROR"),
           "error": (body.get("error") if isinstance(body.get("error"), (dict, str)) else None),
           "output_head": text.strip()[:60]}
    out["checks"].append(rec); print(json.dumps(rec)[:260]); return rec

# --- OpenRouter: key sanity + Authorization-only retry on sane ids
prev = json.loads((HERE / "route_probe_20261102.json").read_text())
or_ids = next((r["model_ids"] for r in prev["routes"] if r["route"] == "openrouter"), [])
print("openrouter catalog:", len(or_ids), "ids")
sane, weird = [], []
for mid in or_ids:
    parts = mid.split("/")
    (weird if len(parts) > 2 else sane).append(mid)
print("  nested ids (look synthetic):", len(weird), "| plain ids:", len(sane))
print("  plain sample:", sane[:12])

for kname in ("OPENROUTER_API_KEY", "OPENROUTER_API_KEY_B", "OPENROUTER_API_KEY_C"):
    key = os.environ.get(kname, "").strip()
    print(f"  {kname}: present={bool(key)} len={len(key)}")
    if not key: continue
    base = "https://openrouter.ai/api/v1"
    for mid in sane[:2]:
        post(base + "/chat/completions",
             {"Authorization": "Bearer " + key, "content-type": "application/json", "User-Agent": UA},
             {"model": mid, "max_tokens": 16, "messages": [{"role": "user", "content": SMOKE}]},
             f"openrouter/{mid} [{kname}]")

# --- APMix at its stated base, ids borrowed from the APINEX catalog
am_key = os.environ.get("APMIX_API_KEY", "").strip()
print("apmix key present:", bool(am_key), "len", len(am_key))
cands = ["claude-opus-5.5", "gpt-6-astra", "gemini-3.1-pro", "claude-sonnet-5.5"]
if am_key:
    for mid in cands[:3]:
        post("https://api.apmix.ai/v1/messages",
             {"x-api-key": am_key, "Authorization": "Bearer " + am_key,
              "anthropic-version": "2023-06-01", "content-type": "application/json", "User-Agent": UA},
             {"model": mid, "max_tokens": 16, "messages": [{"role": "user", "content": SMOKE}]},
             f"apmix/{mid} [anthropic]", shape="anthropic")

out["finished"] = time.time()
(HERE / "route_probe2_20261102.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print("\nWORKING:", [c["label"] for c in out["checks"] if c["status"] == "OK"])
