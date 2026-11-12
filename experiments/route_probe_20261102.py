#!/usr/bin/env python3
"""Route/label reachability probe for P015 replacement labels (2026-11-02).

Metadata GET /models per route plus at most four 16-token off-fixture smoke
calls, in the priority order fixed in AMENDMENT_01: Anthropic-family,
Gemini-family, GPT-family, then any other family. No fixture, no cell slot, no
oracle; nothing here is a session. Keys are never printed or written.
"""
import json, os, re, time
from pathlib import Path
import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
SMOKE = "Reply with exactly one word: READY"

def load_env():
    p = ROOT / ".env"
    if not p.is_file(): return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()

ROUTES = {
  "openrouter": {"base": os.environ.get("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1",
                 "key": os.environ.get("OPENROUTER_API_KEY", "").strip(),
                 "models_paths": ["/models", "/v1/models"], "chat": "/chat/completions"},
  "apmix": {"base": (os.environ.get("APMIX_ANTHROPIC_BASE_URL") or os.environ.get("APMIX_BASE_URL") or "").rstrip("/"),
            "key": os.environ.get("APMIX_API_KEY", "").strip(),
            "models_paths": ["/v1/models", "/models"], "chat": "/v1/messages",
            "fixed_model": os.environ.get("APMIX_MODEL", "").strip()},
}
PRIORITY = [r"anthropic/claude|^claude-", r"google/gemini|^gemini-", r"openai/gpt|^gpt-", r"."]

def headers(key):
    return {"Authorization": "Bearer " + key, "x-api-key": key,
            "anthropic-version": "2023-06-01", "content-type": "application/json",
            "User-Agent": UA}

def inventory(name, r):
    rec = {"route": name, "host": r["base"].split("//")[-1].split("/")[0],
           "key_present": bool(r["key"]), "model_ids": [], "status": "NOT_CONFIGURED"}
    if not r["base"] or not r["key"]:
        return rec
    for path in r["models_paths"]:
        try:
            resp = requests.get(r["base"] + path, headers=headers(r["key"]), timeout=45)
        except requests.RequestException as exc:
            rec.update(status="UNREACHABLE", error=type(exc).__name__); continue
        rec["http_status"] = resp.status_code
        try:
            body = resp.json()
        except ValueError:
            body = {}
        data = body.get("data") or body.get("models") or []
        ids = sorted({x.get("id") for x in data if isinstance(x, dict) and x.get("id")})
        rec["model_ids"] = ids
        rec["status"] = "OK" if resp.ok else "REJECTED"
        if ids: break
    return rec

def smoke_openai(base, key, model, path="/chat/completions"):
    t0 = time.time()
    try:
        resp = requests.post(base + path, headers=headers(key),
            json={"model": model, "max_tokens": 16, "messages": [{"role": "user", "content": SMOKE}]},
            timeout=90, allow_redirects=False)
    except requests.RequestException as exc:
        return {"model": model, "status": "UNREACHABLE", "error": type(exc).__name__}
    latency = round(time.time() - t0, 1)
    try: body = resp.json()
    except ValueError: body = {}
    text = ""
    for ch in (body.get("choices") or []):
        text = ((ch.get("message") or {}).get("content") or "")
        break
    return {"model": model, "http_status": resp.status_code, "latency_s": latency,
            "status": "OK" if (resp.ok and text.strip()) else ("OK_EMPTY" if resp.ok else "HTTP_ERROR"),
            "error": body.get("error") if isinstance(body.get("error"), (dict, str)) else None,
            "output_head": text.strip()[:60]}

def smoke_anthropic(base, key, model):
    t0 = time.time()
    try:
        resp = requests.post(base + "/v1/messages", headers=headers(key),
            json={"model": model, "max_tokens": 16, "messages": [{"role": "user", "content": SMOKE}]},
            timeout=90, allow_redirects=False)
    except requests.RequestException as exc:
        return {"model": model, "status": "UNREACHABLE", "error": type(exc).__name__}
    latency = round(time.time() - t0, 1)
    try: body = resp.json()
    except ValueError: body = {}
    parts = [c.get("text", "") for c in (body.get("content") or []) if isinstance(c, dict)]
    text = "".join(parts)
    return {"model": model, "http_status": resp.status_code, "latency_s": latency,
            "status": "OK" if (resp.ok and text.strip()) else ("OK_EMPTY" if resp.ok else "HTTP_ERROR"),
            "error": body.get("error") if isinstance(body.get("error"), (dict, str)) else None,
            "output_head": text.strip()[:60]}

out = {"probe": "route-probe-20261102", "purpose": "P015 replacement labels; NOT experiment calls",
       "smoke_prompt": SMOKE, "started": time.time(), "routes": [], "smoke": []}

for name, r in ROUTES.items():
    rec = inventory(name, r)
    out["routes"].append(rec)
    print(f"{name:<12} {rec['status']:<14} http={rec.get('http_status')} ids={len(rec['model_ids'])}")
    ids = rec["model_ids"]
    if not ids: continue
    tried = 0
    for pat in PRIORITY:
        for mid in ids:
            if tried >= 4: break
            if not re.search(pat, mid, re.I): continue
            if mid.startswith("free/") and name == "apinex": continue
            res = smoke_openai(r["base"], r["key"], mid, r["chat"]) if r["chat"].startswith("/chat") \
                  else smoke_anthropic(r["base"], r["key"], mid)
            res["route"] = name
            out["smoke"].append(res)
            print("   ", json.dumps(res)[:200])
            tried += 1
        if tried >= 4: break

am = ROUTES["apmix"]
if am["fixed_model"] and am["base"] and am["key"]:
    for fn, label in ((smoke_anthropic, "anthropic_shape"), (smoke_openai, "openai_shape")):
        res = fn(am["base"], am["key"], am["fixed_model"])
        res.update(route="apmix", shape=label)
        out["smoke"].append(res)
        print("    apmix", label, json.dumps(res)[:200])

out["finished"] = time.time()
(HERE / "route_probe_20261102.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print("\nWORKING LABELS:", [s["model"] for s in out["smoke"] if s["status"] == "OK"])
