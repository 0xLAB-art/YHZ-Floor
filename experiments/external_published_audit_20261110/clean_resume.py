import json
rows = [l for l in open("results.jsonl") if l.strip()]
keep = [l for l in rows if json.loads(l).get("status") != "PROVIDER_UNAVAILABLE"]
open("results.jsonl", "w").writelines(keep)
print(f"kept {len(keep)}/{len(rows)}")
