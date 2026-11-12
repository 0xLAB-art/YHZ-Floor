#!/usr/bin/env python3
"""Run the blind GPT-family review via the agentrouter gateway.

The route is Anthropic-messages-compatible (per the frozen project adapters:
provider_adapter_agentrouter_p017.py): POST {base}/v1/messages with x-api-key +
Bearer + anthropic-version + the claude-cli User-Agent the route requires.
Usage: AGENTROUTER_API_KEY=... AGENTROUTER_BASE_URL=https://agentrouter.org \
       python3 -I run_gpt_review.py MODEL [MODEL...]
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = os.environ.get("AGENTROUTER_BASE_URL", "https://agentrouter.org").rstrip("/")
KEY = os.environ.get("AGENTROUTER_API_KEY", "")
UA = "claude-cli/2.0.0 (external, cli)"
if not KEY:
    sys.exit("set AGENTROUTER_API_KEY")

prompt_tpl = (HERE/'PROMPT_REVIEW.md').read_text()
payload = (HERE/'review_payload.json').read_text()
prompt = prompt_tpl.replace('{PAYLOAD}', payload)
print(f"prompt chars: {len(prompt)}", flush=True)

def call(model, max_tokens=16000, timeout=420, retries=2):
    body = json.dumps({"model": model, "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(
        f"{BASE}/v1/messages", data=body,
        headers={"x-api-key": KEY, "Authorization": "Bearer " + KEY,
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json",
                 "User-Agent": UA})
    last = None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            text = "".join(b.get("text", "") for b in data.get("content", [])
                           if b.get("type") == "text")
            return {"ok": True, "elapsed_s": round(time.time()-t0, 1),
                    "usage": data.get("usage"), "stop_reason": data.get("stop_reason"),
                    "content": text}
        except urllib.error.HTTPError as e:
            detail = ""
            try: detail = e.read().decode()[:300]
            except Exception: pass
            last = {"ok": False, "error": f"HTTP {e.code}: {detail}",
                    "elapsed_s": round(time.time()-t0, 1)}
            if e.code in (429, 500, 502, 503, 529) and attempt < retries:
                time.sleep(20); continue
            return last
        except Exception as e:
            last = {"ok": False, "error": f"{type(e).__name__}: {e}"[:300],
                    "elapsed_s": round(time.time()-t0, 1)}
            if attempt < retries:
                time.sleep(15); continue
    return last

for model in sys.argv[1:]:
    out = HERE/'outputs'/f'{model.replace("/","_")}.json'
    print(f"calling {model} ...", flush=True)
    r = call(model)
    out.write_text(json.dumps({"model": model, "base": BASE + "/v1/messages",
                               "recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                               **r}, indent=1))
    if r.get("ok"):
        print(f"  ok in {r['elapsed_s']}s, content {len(r['content'])} chars, usage {r.get('usage')}")
    else:
        print(f"  FAILED: {r.get('error')}")
