#!/usr/bin/env python3
"""Provider/model inventory probe (2026-11-02).

Purpose: enumerate which model labels are actually reachable on each configured
route BEFORE any preregistration names them, so a cross-label cohort is
registered against a measured inventory rather than a guessed one.

This makes NO experiment call: it issues GET /v1/models per route (metadata
only). No key material is printed or written; only route host, HTTP status, and
provider-reported model ids are recorded.

Output: research_execution/labels_probe_20261102.json
"""
import hashlib
import json
import os
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent      # sp2027/research_execution
ROOT = HERE.parents[1]                       # repository root (holds gitignored .env)
ENV = ROOT / ".env"
UA = "claude-cli/2.0.0 (external, cli)"  # routers reject default python UA

ROUTES = {
    # name: (base_url_env, key_env)
    "agentrouter": ("AGENTROUTER_BASE_URL", "AGENTROUTER_API_KEY"),
    "apmix": ("APMIX_BASE_URL", "APMIX_API_KEY"),
    "apmix_anthropic": ("APMIX_ANTHROPIC_BASE_URL", "APMIX_API_KEY"),
    "apinex": ("APINEX_BASE_URL", "APINEX_API_KEY"),
    "openrouter": ("OPENROUTER_BASE_URL", "OPENROUTER_API_KEY"),
}


def load_env():
    if not ENV.is_file():
        return
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def probe(route, base_env, key_env):
    base = os.environ.get(base_env, "").rstrip("/")
    key = os.environ.get(key_env, "").strip()
    rec = {"route": route, "base_url_env": base_env, "key_env": key_env,
           "key_present": bool(key), "base_present": bool(base)}
    if not base or not key:
        rec["status"] = "NOT_CONFIGURED"
        return rec
    rec["host"] = base.split("//")[-1].split("/")[0]
    for path in ("/v1/models", "/models"):
        try:
            r = requests.get(base + path, headers={
                "x-api-key": key, "Authorization": "Bearer " + key,
                "anthropic-version": "2023-06-01", "User-Agent": UA}, timeout=30)
        except requests.RequestException as exc:
            rec.update(status="UNREACHABLE", error=type(exc).__name__,
                       path=path, at=time.time())
            continue
        rec["path"] = path
        rec["http_status"] = r.status_code
        body = None
        try:
            body = r.json()
        except ValueError:
            rec["body_sha256"] = hashlib.sha256(r.content).hexdigest()
            rec["body_bytes"] = len(r.content)
        if isinstance(body, dict):
            data = body.get("data") or body.get("models") or []
            ids = [x.get("id") for x in data if isinstance(x, dict) and x.get("id")]
            rec["status"] = "OK" if r.ok else "REJECTED"
            rec["model_count"] = len(ids)
            rec["model_ids"] = sorted(ids)[:400]
            if not ids:
                rec["body_keys"] = sorted(body.keys())[:20]
        else:
            rec["status"] = "OK_NON_JSON" if r.ok else "REJECTED"
        if r.ok:
            break
    rec.setdefault("at", time.time())
    return rec


def main():
    load_env()
    out = {"probe": "labels-probe-20261102", "purpose": "pre-registration inventory; no experiment call",
           "user_agent": UA, "started": time.time(), "routes": []}
    for name, (b, k) in ROUTES.items():
        out["routes"].append(probe(name, b, k))
    out["finished"] = time.time()
    (HERE / "labels_probe_20261102.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    for r in out["routes"]:
        ids = r.get("model_ids", [])
        print(f"{r['route']:<18} {r.get('status'):<14} http={r.get('http_status')} "
              f"models={len(ids)}")
        for m in ids[:40]:
            print("    ", m)
        if len(ids) > 40:
            print(f"     ... +{len(ids)-40} more")


if __name__ == "__main__":
    main()
