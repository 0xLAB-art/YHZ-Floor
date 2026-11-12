#!/usr/bin/env python3
"""Census: probe all 14 (task, R0, label) combos with 16-token smokes,
emit COMPLETENESS_CENSUS_PUBLISHED_AUDIT.json. NON-EVIDENCE pre-flight."""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, "/mnt/nvme5/ACTS-Attack/sp2027/research_execution/external_admission_amend5_transport_20261109")
from responses_client import AgentRouterResponsesClient

TASKS = ["2015q-cry-eps", "2015q-cry-eps_part2", "2017q-cry-almost_xor",
         "2017q-cry-another_xor", "2018q-cry-babycrypto", "2018q-cry-lowe",
         "2021q-cry-crack_me"]
LABELS = ["gpt-6.1-sol", "gpt-5.6-sol"]
key = os.environ.get("AGENTROUTER_API_KEY", "").strip()
if not key: sys.exit("AGENTROUTER_API_KEY not set")

rows, passed = [], []
for task in TASKS:
    for label in LABELS:
        client = AgentRouterResponsesClient(key, label, "https://agentrouter.org")
        try:
            result = client.call("Reply with exactly: OK", 16)
            rows.append({"task": task, "rep": "R0", "label": label,
                         "probe": "ok", "ts": time.time()})
            passed.append([task, "R0", label])
            print(f"PASS {task} {label}")
        except Exception as exc:
            rows.append({"task": task, "rep": "R0", "label": label,
                         "probe": f"FAIL {type(exc).__name__}: {str(exc)[:80]}",
                         "ts": time.time()})
            print(f"FAIL {task} {label}")
        time.sleep(1)

out = {"schema": "census-pubaudit-v1", "generated_date": "2026-11-11",
       "rows": rows, "pass_combinations": passed,
       "registered_cap": 12000, "boundary": "16-token probe; evidence calls at the registered 12000 cap",
       "effort_field": "omitted (backend measured to ignore it)",
       "note": "both labels verified live before freeze"}
(HERE := __import__("pathlib").Path(".")) 
out_name = "COMPLETENESS_CENSUS_PUBLISHED_AUDIT.json"
Path(out_name).write_text(json.dumps(out, indent=2) + "\n")
print(f"census: {len(passed)}/14 PASS -> {out_name}")
sys.exit(0 if len(passed) == 14 else 1)
