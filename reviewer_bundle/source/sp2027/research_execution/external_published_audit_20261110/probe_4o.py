#!/usr/bin/env python3
import os, sys
sys.path.insert(0, "/mnt/nvme5/ACTS-Attack/sp2027/research_execution/external_admission_amend5_transport_20261109")
from responses_client import AgentRouterResponsesClient
key = os.environ.get("APINEX_API_KEY", "").strip()
for model in ["gpt-4o", "gpt-4o-2024-11-20", "gpt-4o-mini", "gpt-4.1"]:
    client = AgentRouterResponsesClient(key, model, "https://agentrouter.org")
    try:
        result = client.call("Reply with exactly: OK", 64)
        text = (result.get("text") or "")[:20].replace("\n", " ")
        print(f"OK   {model}: {text!r}")
    except Exception as exc:
        print(f"FAIL {model}: {type(exc).__name__}: {str(exc)[:90]}")
