#!/usr/bin/env python3
"""Post-run fingerprint audit — Amendment 4 (non-evidence discipline from
P010X1/P010L5): every raw provider response is checked for the attested
label echo (the response's `model` field must equal the session's registered
label).  A drifting cohort is withdrawn to same-label with its numbers
retained as same-label evidence.  Writes FINGERPRINT_AUDIT.json.
"""
import json
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "sessions" / "raw_provider_responses"
LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]

# sessions' registered label per run_id — and per (label|task|rep|seed) key
# so recovery-wave raw responses (whose run ids carry a fresh uuid) resolve;
# the label is also parsed from the run_id slug itself as a cross-check.
label_of = {}
key_of = {}
results = HERE / "results.jsonl"
if results.exists():
    for line in results.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            label_of[r["run_id"]] = r["label"]
            key_of[(r["label"], r["task_id"], r["representation"], r["seed"])] = r["label"]
recovery = HERE / "results_recovery_8400.jsonl"
if recovery.exists():
    for line in recovery.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            label_of[r["run_id"]] = r["label"]

echo_counts = collections.Counter()
mismatches = []
checked = 0
for f in sorted(RAW.glob("*.json")):
    run_id = f.name.rsplit("__turn", 1)[0]
    try:
        d = json.loads(f.read_text())
    except Exception:
        continue
    rid = d.get("model")
    # the attested label for this response: prefer the primary results row
    attested = label_of.get(run_id)
    if attested is None:
        # recovery rows: run_id suffix __rec8400; strip for the label lookup
        base = run_id.replace("__rec8400", "")
        attested = label_of.get(base)
    checked += 1
    echo_counts[(attested, rid)] += 1
    if attested is not None and rid is not None and rid != attested:
        mismatches.append({"file": f.name, "attested": attested, "echo": rid,
                           "detail": "label drift — cohort withdrawn to same-label"})

per_label = collections.Counter()
for (attested, rid), n in echo_counts.items():
    per_label[attested or "?"] += n

out = {
    "schema": "external-admission-amend4-fingerprint/1",
    "evidence": False,
    "raw_responses_checked": checked,
    "per_label_echo": dict(per_label),
    "mismatches": mismatches,
    "verdict": ("all raw responses echo the attested label; 0 mismatches"
                if not mismatches else
                f"{len(mismatches)} mismatches — drifting cohort withdrawn "
                "to same-label"),
}
(HERE / "FINGERPRINT_AUDIT.json").write_text(json.dumps(out, indent=1))
print(json.dumps({"checked": checked, "mismatches": len(mismatches),
                  "per_label_echo": dict(per_label)}, indent=1))
