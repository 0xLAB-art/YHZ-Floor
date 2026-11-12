#!/usr/bin/env bash
# One-shot diagnostic: same C2 prompt that produced an empty at the 4200 floor,
# sent once at max_tokens=8000. Recorded as diagnostics, not part of any cohort.
set -euo pipefail
cd /mnt/nvme5/ACTS-Attack
PROMPT_DIR=/mnt/nvme5/ACTS-Attack/sp2027/research_execution
set -a; source .env; set +a
PROMPT_FILE="$PROMPT_DIR/info_contract_aesgcm_random_p021ar_20261103/prompts/info_contract_aesgcm_random_p021ar_20261103__C2__seed_5434183162525103062__1b57f44fc462__turn1.txt"
python3 - "$PROMPT_FILE" << 'PY'
import json, os, sys, urllib.request
prompt=open(sys.argv[1]).read()
body={"model": os.environ.get("AGENTROUTER_LABEL_MODEL","gpt-6-astra"),
      "max_tokens": 8000,
      "messages":[{"role":"user","content":prompt}]}
req=urllib.request.Request("https://agentrouter.org/v1/messages",
    data=json.dumps(body).encode(),
    headers={"x-api-key": os.environ["AGENTROUTER_API_KEY"],
             "anthropic-version":"2023-06-01","content-type":"application/json"})
with urllib.request.urlopen(req, timeout=600) as r:
    b=json.loads(r.read())
usage=b.get("usage",{})
print("stop_reason:", b.get("stop_reason"))
print("usage:", {k:v for k,v in usage.items() if v is not None and k!="server_tool_use"})
content=b.get("content",[])
print("blocks:", [(c.get("type"), len(str(c.get("text") or ""))) for c in content])
txt="".join(c.get("text","") for c in content if c.get("type")=="text")
print("text_len:", len(txt))
print("text_head:", txt[:200].replace("\n"," "))
PY
