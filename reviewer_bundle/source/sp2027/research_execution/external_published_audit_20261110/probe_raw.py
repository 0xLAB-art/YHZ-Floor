#!/usr/bin/env python3
"""Raw-response probe across known gateways. Key from env; body previews only."""
import json, os, urllib.request, urllib.error
key = os.environ.get("APINEX_API_KEY", "").strip()
for base, path, model in [
    ("https://api.apinex.bond", "/v1/chat/completions", "free/gpt-6-luna"),
    ("https://agentrouter.org", "/v1/chat/completions", "free/gpt-6-luna"),
    ("https://agentrouter.org", "/v1/responses", "gpt-6.1-sol"),
]:
    payload = {"model": model, "max_tokens": 16,
               "messages": [{"role": "user", "content": "Reply with exactly: OK"}]}
    if path.endswith("/responses"):
        payload = {"model": model, "max_output_tokens": 16,
                   "input": "Reply with exactly: OK"}
    r = urllib.request.Request(base + path, method="POST",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) research-audit-client"})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            body = resp.read().decode()[:400]
            print(f"{base}{path} [{model}] -> {resp.status}\n  {body}\n")
    except urllib.error.HTTPError as e:
        print(f"{base}{path} [{model}] -> HTTP {e.code}\n  {e.read().decode()[:400]}\n")
    except Exception as e:
        print(f"{base}{path} [{model}] -> {type(e).__name__}: {e}\n")
