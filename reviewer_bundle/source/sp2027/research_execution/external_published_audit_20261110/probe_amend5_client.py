#!/usr/bin/env python3
"""Probe the new key through the exact amend5 responses client (36/36 route)."""
import os, sys
sys.path.insert(0, "/mnt/nvme5/ACTS-Attack/sp2027/research_execution/external_admission_amend5_transport_20261109")
from responses_client import AgentRouterResponsesClient

key = os.environ.get("APINEX_API_KEY", "").strip()
for model in ["gpt-6.1-sol", "gpt-5.6-sol", "free/gpt-6-luna"]:
    client = AgentRouterResponsesClient(key, model, "https://agentrouter.org")
    try:
        result = client.call("Reply with exactly: OK", 16)
        text = (result.get("text") or "")[:20].replace("\n", " ")
        print(f"OK   {model}: {text!r}")
    except Exception as exc:
        print(f"FAIL {model}: {type(exc).__name__}: {str(exc)[:110]}")
