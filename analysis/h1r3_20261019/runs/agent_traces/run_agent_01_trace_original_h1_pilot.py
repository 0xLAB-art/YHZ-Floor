#!/usr/bin/env python3
"""Agent 1 of 5: trace Original 72-session H1 replacement pilot defects.

Mission:
- Read the retained replacement-pilot artifacts.
- Reconstruct the exact failure/contrast issues already recorded.
- Do NOT start provider calls.
- Write a structured trace JSON under sp2027/analysis/h1r3_20261019/runs/agent_traces/.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path("sp2027/analysis")
HERE = ROOT / "h1r3_20261019"
TRACE_DIR = HERE / "runs" / "agent_traces"
TRACE_DIR.mkdir(parents=True, exist_ok=True)

TRACT = {
    "agent": "trace_agent_01_original_h1_replacement_pilot",
    "scope": "original 72-session replacement pilot artifacts only",
    "provider_calls": False,
    "started_utc": json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()),
}

disposition = HERE / "H1_FINAL_DISPOSITION.md"
TRACT["has_H1_FINAL_DISPOSITION"] = disposition.exists()

summary_paths = [
    ROOT / "contract_sound_agent_replacement_20261018" / "AGENT_PILOT_RESULTS_SUMMARY.json",
    ROOT / "contract_sound_agent_replacement_20261018" / "AGENT_PILOT_PAIRED_RESULTS.json",
]
found_summaries = [str(p) for p in summary_paths if p.exists()]
TRACT["found_summaries"] = found_summaries

replay_paths = [
    ROOT / "contract_sound_replacement_readiness_20261018" / "PAIRED_C1_C2_REPLAY_TABLE.json",
    ROOT / "contract_sound_replacement_readiness_20261018" / "C0_AUDIT.json",
]
found_replays = [str(p) for p in replay_paths if p.exists()]
TRACT["found_replay_tables"] = found_replays

def load(p):
    try:
        return json.loads(p.read_text())
    except Exception as e:
        return {"_load_error": str(e)}

c1c2 = []
c0 = []
if found_replays:
    c1c2 = load(Path(found_replays[0]))
    if len(found_replays) > 1:
        c0 = load(Path(found_replays[1]))

def count(rows, key, value):
    if not isinstance(rows, list):
        return 0
    return sum(1 for r in rows if isinstance(r, dict) and r.get(key) == value)

def count_nested(rows, parent, key, value):
    if not isinstance(rows, list):
        return 0
    n = 0
    for r in rows:
        if isinstance(r, dict) and isinstance(r.get(parent), dict):
            if r[parent].get(key) == value:
                n += 1
    return n

TRACT["paired_c1c2_rows"] = len(c1c2) if isinstance(c1c2, list) else None
TRACT["c0_rows"] = len(c0) if isinstance(c0, list) else None

if isinstance(c1c2, list):
    TRACT["paired_counts"] = {
        "c1_executed": count_nested(c1c2, "c1", "execution", "EXECUTED"),
        "c2_executed": count_nested(c1c2, "c2", "execution", "EXECUTED"),
        "c2_sandbox_rejected": count_nested(c1c2, "c2", "execution", "SANDBOX_REJECTED"),
        "c2_execution_failed": count_nested(c1c2, "c2", "execution", "EXECUTION_FAILED"),
        "c1_reference_accepted": count_nested(c1c2, "c1", "reference", "ACCEPTED"),
        "c2_reference_accepted": count_nested(c1c2, "c2", "reference", "ACCEPTED"),
    }

if isinstance(c0, list):
    TRACT["c0_rejected"] = count(c0, "reference_verdict", "REJECTED")
    TRACT["c0_unexplained_acceptance"] = count(c0, "unexplained_acceptance", True)

fail_session_lines = []
if disposition.exists():
    txt = disposition.read_text()
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("Session ") and "-" in s and len(s) < 120:
            fail_session_lines.append(s)
TRACT["failure_session_lines_in_disposition"] = fail_session_lines[:20]

TRACT["critical_issues_traced"] = [
    {
        "type": "source_qualification_failure_not_crypto_failure",
        "where": "H1_FINAL_DISPOSITION.md §4",
        "recorded_sessions": [
            "replacement-005-8163a4307df9",
            "replacement-013-d23672d9f3fe",
        ],
        "issue": "C2 losses were pre-execution sandbox/source-qualification rejections, not oracle/cryptographic rejections",
        "note": "AST found unused hashlib import; programs never executed; thus C1-C2 contrast contaminated by interface/qualification failure",
    },
    {
        "type": "contrast_not_representation_only",
        "where": "72_EXPERIMENT_DESIGN_VALIDITY_AUDIT.md",
        "issue": "C1 and C2 differed in prompt label, encoding family, prompt length, and decoding burden, not only representation",
        "note": "Does not isolate representation as a single independent variable",
    },
    {
        "type": "sampling_controls_not_documented",
        "where": "72_EXPERIMENT_DESIGN_VALIDITY_AUDIT.md and repair protocol",
        "issue": "Request rows recorded only model + max_tokens; temperature/top_p/seed/system/stop not captured",
        "note": "Model stochasticity remains an explicit limitation",
    },
    {
        "type": "c0_endpoint_mismatch",
        "where": "72_EXPERIMENT_DESIGN_VALIDITY_AUDIT.md §7 and repair protocol",
        "issue": "C0 required UNDERDETERMINED abstention JSON, a different predicate/endpoint than C1/C2",
        "note": "C0 outcomes cannot be read on the C1/C2 scale",
    },
    {
        "type": "global_randomization_weak",
        "where": "72_EXPERIMENT_DESIGN_VALIDITY_AUDIT.md and repair protocol",
        "issue": "Randomization was only C1/C2 order within each seed pair; block order was ECDSA -> ChaCha20 -> C0",
        "note": "No global randomization across the full schedule",
    },
    {
        "type": "small_effective_sample_for_claimed_effect",
        "where": "H1_FINAL_DISPOSITION.md §8 and repair protocol §10",
        "issue": "With 24 pairs, power for a true 0.25 effect is materially limited under the relevant discordance scenarios",
        "note": "A non-significant result is inconclusive, not equivalence",
    },
]

TRACT["stop_rule_applied"] = "No provider calls; trace-only from retained artifacts."
TRACT["completed_utc"] = json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())

out = TRACE_DIR / "agent_01_trace_original_h1_replacement_pilot.json"
out.write_text(json.dumps(TRACT, indent=2, sort_keys=False) + "\n")
print(json.dumps(TRACT, indent=2, sort_keys=False))
