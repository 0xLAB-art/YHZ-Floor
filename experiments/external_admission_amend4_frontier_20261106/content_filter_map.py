#!/usr/bin/env python3
"""Content-filter characterization — Amendment 4 (measurement, not a defect
claim): which (label, task, representation) slots were blocked pre-output by
the gateway's content filter (HTTP 400 content-blocked), from the event
ledger + session rows.  The filter is a transport-layer owner candidate: it
shapes which denominators exist at all.  Writes CONTENT_FILTER_MAP.json.
"""
import json
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent

rows = [json.loads(l) for l in (HERE / "results.jsonl").read_text().splitlines() if l.strip()]
ev = []
evf = HERE / "sessions" / "events" / "events_amend4.jsonl"
if evf.exists():
    ev = [json.loads(l) for l in evf.read_text().splitlines() if l.strip()]

blocked_by = collections.Counter()
for e in ev:
    if e["kind"] == "provider_failure" and "content-blocked" in e.get("detail", ""):
        run = e["run_id"]
        blocked_by[run] += 1

# map run_id -> (label, task, rep)
slot = {}
for r in rows:
    slot[r["run_id"]] = (r["label"], r["task_id"], r["representation"], r["status"])

block_grid = collections.Counter()
for run, n in blocked_by.items():
    lab, task, rep, st = slot.get(run, ("?", "?", "?", "?"))
    block_grid[(lab, task.split("cry-")[-1], rep)] += 1

session_blocks = collections.Counter()
for r in rows:
    if r["status"] == "PROVIDER_UNAVAILABLE" and "content" in (r.get("provider_failure_detail") or ""):
        session_blocks[(r["label"], r["task_id"].split("cry-")[-1], r["representation"])] += 1

cells = {}
for (lab, task, rep), n in sorted(session_blocks.items()):
    cells.setdefault(lab, {}).setdefault(task, {})[rep] = n

out = {
    "schema": "external-admission-amend4-filter-map/1",
    "note": ("transport-layer content filter (HTTP 400 content-blocked); "
             "recorded as a measurement of which denominators exist; no "
             "benchmark-quality claim"),
    "blocked_provider_failure_events": sum(blocked_by.values()),
    "session_slots_blocked_by_cell": cells,
    "boundary": ("the filter shapes denominators, not outcomes; blocked "
                 "slots are excluded from acceptance denominators per the "
                 "registered two-sided rule"),
}
(HERE / "CONTENT_FILTER_MAP.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out["session_slots_blocked_by_cell"], indent=1))
