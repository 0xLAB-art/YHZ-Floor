#!/usr/bin/env python3
"""Fresh, bounded provider-route attestation for ACTS Stage 4.

One call only, exact approved route, no retry, no fallback. The raw API key and
response headers are never written. Provider response text is retained because
it is the experimental output of this harmless attestation prompt.
"""
from __future__ import annotations
import hashlib
import json
import os
import time
from pathlib import Path

import requests

OUT = Path(__file__).with_name("provider_attestation.json")
BASE = os.environ.get("ANTHROPIC_BASE_URL", "https://api.apmix.ai").rstrip("/")
MODEL = os.environ.get("APMIX_MODEL", "claude-sonnet-4-6-free")
KEY = os.environ.get("APMIX_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
EXPECTED_BASE = "https://api.apmix.ai"
EXPECTED_MODEL = "claude-sonnet-4-6-free"
PROMPT = (
    'Return exactly this JSON and nothing else: '
    '{"route_attestation":"ok","requested_model":"claude-sonnet-4-6-free"}'
)

if OUT.exists():
    raise SystemExit(f"refusing to overwrite {OUT}")
if BASE != EXPECTED_BASE:
    raise SystemExit(f"unexpected base URL: {BASE!r}")
if MODEL != EXPECTED_MODEL:
    raise SystemExit(f"unexpected model route: {MODEL!r}")
if not KEY:
    raise SystemExit("approved APMIX credential is not exported")

payload = {
    "model": MODEL,
    "max_tokens": 100,
    "temperature": 0,
    "messages": [{"role": "user", "content": PROMPT}],
}
headers = {
    "x-api-key": KEY,
    "Authorization": "Bearer " + KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}
started = time.time()
response = requests.post(BASE + "/v1/messages", headers=headers, json=payload, timeout=120)
finished = time.time()
body = response.json()
parts = body.get("content", []) if isinstance(body, dict) else []
text = "".join(x.get("text", "") for x in parts if isinstance(x, dict) and x.get("type") == "text")
record = {
    "schema": "acts-stage4-provider-attestation/1",
    "endpoint": BASE + "/v1/messages",
    "requested_model": MODEL,
    "provider_model": body.get("model") if isinstance(body, dict) else None,
    "http_status": response.status_code,
    "provider_object": body.get("type") or body.get("object") if isinstance(body, dict) else None,
    "stop_reason": body.get("stop_reason") if isinstance(body, dict) else None,
    "usage": body.get("usage", {}) if isinstance(body, dict) else {},
    "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
    "response_sha256": hashlib.sha256(response.content).hexdigest(),
    "output_sha256": hashlib.sha256(text.encode()).hexdigest(),
    "output_text": text,
    "elapsed_seconds": round(finished - started, 6),
    "no_retry": True,
    "no_fallback": True,
    "credential_recorded": False,
    "route_match": body.get("model") == EXPECTED_MODEL if isinstance(body, dict) else False,
}
OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
print(json.dumps({k: record[k] for k in ("http_status", "requested_model", "provider_model", "route_match", "usage")}, indent=2))
if response.status_code != 200 or not record["route_match"] or not text:
    raise SystemExit(1)