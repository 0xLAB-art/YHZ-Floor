#!/usr/bin/env python3
"""Build FREEZE.json — Amendment 5 (transport-repaired panel, 2026-11-09).

Hashes every frozen input of the Amendment-5 bundle plus the read-only basis
files (the Amendment-4 transport-decomposition finding and audit JSON that
motivate this protocol; the Amendment-4 runner this protocol inherits the
frozen machinery from), records the design (3 labels, census-defined plan,
12000-token cap with the effort field omitted, 4 turns with captured-output
feedback, dual codings, CRASH class + COMPLETION_TRUNCATED provider class,
token ceiling) and the executed pre-freeze census, and writes FREEZE.json.
The namespace-restricted freeze commit is the registration act. The live
runner refuses to run without FREEZE_COMMIT.txt.
"""

import hashlib
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "FREEZE.json"
AM4 = HERE.parent / "external_admission_amend4_frontier_20261106"

EXCLUDE = {
    "FREEZE.json", "FREEZE_COMMIT.txt", "build_freeze_amend5.py",
    "HEALTH.json", "results.jsonl", "COMPLETENESS_CENSUS_stream.jsonl",
}

LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]
SEEDS = [425, 426, 427, 428]
MAX_OUTPUT_TOKENS = 12_000
REASONING_EFFORT = None
MAX_TURNS = 4


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def group_for(rel):
    if rel.startswith("PREREGISTRATION"):
        return "prereg_and_records"
    if rel.startswith("census_nyu/") or rel.startswith("oracle/"):
        return "census_and_oracle"
    if rel.startswith("fixtures/rt_transform/"):
        return "prompts"
    if rel.startswith("fixtures/tasks/"):
        return "artifacts"
    if rel in ("PROMPT_HASHES.json", "seed_sweep_AMEND5_SEED_SWEEP.json"):
        return "manifests"
    if rel.startswith("COMPLETENESS_CENSUS"):
        return "census_amend5"
    if rel in ("run_amend5_sessions.py", "responses_client.py",
               "completeness_census_amend5.py", "assemble_census_amend5.py"):
        return "harness"
    return "other"


def main() -> int:
    census = json.loads((HERE / "COMPLETENESS_CENSUS_AMEND5.json").read_text())
    files = {}
    for p in sorted(HERE.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(HERE).as_posix()
        if rel in EXCLUDE or rel.startswith("sessions/") or \
                rel.startswith("__pycache__/"):
            continue
        files[rel] = {"sha256": sha(p), "group": group_for(rel)}
    for rel in ("FINDING_TRANSPORT_DECOMPOSITION.md",
                "AUDIT_TRANSPORT_DECOMPOSITION.json",
                "audit_transport_decomposition.py",
                "run_amend4_sessions.py"):
        ap = AM4 / rel
        if ap.is_file():
            files["../external_admission_amend4_frontier_20261106/" + rel] = {
                "sha256": sha(ap),
                "path": ("external_admission_amend4_frontier_20261106/" + rel),
                "group": "read_only_basis_amend4"}
    freeze = {
        "schema": "external-admission-amend5-freeze/1",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "FROZEN — awaiting namespace-restricted commit",
        "protocol": "PHASE2-EXTERNAL-ADMISSION-AMEND5-TRANSPORT-v1",
        "design": {
            "labels": LABELS,
            "seeds": SEEDS,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "reasoning_effort": REASONING_EFFORT,
            "temperature_field": "omitted (route constraint precedent)",
            "turns": MAX_TURNS,
            "transport": "agentrouter /v1/responses (OpenAI Responses API)",
            "plan_source": "COMPLETENESS_CENSUS_AMEND5.json pass_combinations",
            "plan_sessions": census["grid_sessions"],
            "plan_pass_combinations": len(census["pass_combinations"]),
            "blocked_pairs_frozen": census["frozen_blocked_pairs"],
            "codings": ["C1 whole-stdout == pin (primary)",
                        "C2 first flag-shaped token == pin"],
            "status_classes": ["SUCCESS", "CRASH", "ORACLE_FAIL", "TIMEOUT",
                               "AGENT_GIVEUP", "MODEL_REFUSAL",
                               "TOOL_FAILURE", "PROVIDER_UNAVAILABLE",
                               "COMPLETION_TRUNCATED", "HARNESS_ERROR"],
            "feedback": ("turns>1 carry captured stdout tail (<=600) and "
                         "stderr tail (<=600); parse failures carry the "
                         "registered REVISION REQUEST"),
            "output_token_ceiling": 2_500_000,
            "output_token_checkpoint": 2_000_000,
        },
        "gates_executed_before_freeze": {
            "compat_gate_v1": "COMPAT_GATE_AMEND5.json (old calibration; "
                              "measured the filter set and the 4200-cap "
                              "rumination regime)",
            "completeness_census": "COMPLETENESS_CENSUS_AMEND5.json "
                                   "(registered (pair, label) map at cap "
                                   "12000, effort field omitted)",
            "filter_replications": ("thrice-replicated: messages wave "
                                    "2026-11-07, responses re-probe "
                                    "2026-11-09, funded account 2026-11-09"),
        },
        "files": files,
    }
    OUT.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": freeze["status"],
        "files": len(files),
        "groups": sorted({g["group"] for g in files.values()}),
        "plan_pass_combinations": census["pass_combinations"],
        "plan_sessions": census["grid_sessions"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
