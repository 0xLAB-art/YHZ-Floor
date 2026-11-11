#!/usr/bin/env python3
"""Gateway probe v2 — through the house ApinexClient (exact runner code path).
NON-EVIDENCE; key from env, never logged; 16-token smokes only."""
import os, sys, time
sys.path.insert(0, "/mnt/nvme5/ACTS-Attack/sp2027/research_execution/external_admission_amend3_20261105")
from apinex_client import ApinexClient

key = os.environ.get("APINEX_API_KEY", "").strip()
if not key: sys.exit("APINEX_API_KEY not set")

LABELS = ["free/gpt-6-luna", "free/qwen-3.8-max", "free/deepseek-v4.1-flash",
          "gpt-6.1-sol", "gpt-5.6-sol", "gpt-4o", "gpt-4o-2024-11-20", "gpt-4o-mini"]
for label in LABELS:
    client = ApinexClient(key, label)
    try:
        result = client.call("Reply with exactly: OK", 16)
        usage = (result.get("metadata") or {}).get("usage") or {}
        text = (result.get("text") or "")[:20].replace("\n", " ")
        print(f"OK   {label}: {text!r} usage={ {k: usage.get(k) for k in ('total_tokens','cost') if usage.get(k) is not None} }")
    except Exception as exc:
        msg = str(exc)[:100].replace("\n", " ")
        print(f"FAIL {label}: {type(exc).__name__}: {msg}")
    time.sleep(1)
