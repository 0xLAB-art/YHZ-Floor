#!/usr/bin/env python3
"""Freeze: build FREEZE.json for PHASE2-EXTERNAL-PUBLISHED-AUDIT-v1.
Zero model calls, zero network. Refuses without the census."""
import hashlib, json, sys, time
from pathlib import Path
HERE = Path("."); OUT = HERE / "FREEZE.json"
TOP = ["PREREGISTRATION_PUBLISHED_AUDIT.md", "run_published_audit_sessions.py",
       "responses_client.py", "census_pubaudit.py", "COMPLETENESS_CENSUS_PUBLISHED_AUDIT.json",
       "PROMPT_HASHES.json", "seed_sweep_PUBLISHED_AUDIT.json", "oracle/answers.json"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
census = json.loads((HERE / "COMPLETENESS_CENSUS_PUBLISHED_AUDIT.json").read_text())
if not census.get("pass_combinations"): sys.exit("census registers no PASS combination")
files = {}
for name in TOP:
    p = HERE / name
    if not p.is_file(): sys.exit(f"missing frozen input: {name}")
    files[name] = {"sha256": sha(p)}
manifest = json.loads((HERE / "PROMPT_HASHES.json").read_text())
for e in manifest["instantiated_prompts"]:
    files[e["path"]] = {"sha256": e["sha256"]}
for task, arts in manifest["artifacts"].items():
    for a in arts:
        rel = f"fixtures/tasks/{task}/{a['name']}"
        p = HERE / rel
        if not p.is_file(): sys.exit(f"missing artifact: {rel}")
        if sha(p) != a["sha256"]: sys.exit(f"artifact hash mismatch: {rel}")
        files[rel] = {"sha256": a["sha256"]}
for e in manifest["instantiated_prompts"]:
    if not (HERE / e["path"]).is_file(): sys.exit(f"missing prompt: {e['path']}")
OUT.write_text(json.dumps({"namespace": HERE.name, "status": "FROZEN 2026-11-11 (pre-launch registration)",
    "registered_date": "2026-11-11", "files": files,
    "note": "registered inputs of PHASE2-EXTERNAL-PUBLISHED-AUDIT-v1; the runner re-verifies every hash at live start"}, indent=2) + "\n")
print(f"FROZEN: {len(files)} inputs hashed -> FREEZE.json")
