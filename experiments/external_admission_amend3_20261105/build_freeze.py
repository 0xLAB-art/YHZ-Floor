#!/usr/bin/env python3
"""Build FREEZE.json — Amendment 3 (2026-11-05).

Hashes every frozen input of the Amendment-3 bundle plus the read-only basis
APMIX client, records the design (3-label APINEX free panel) and the executed
pre-freeze gates, and writes FREEZE.json.  The namespace-restricted freeze
commit is the registration act; this file records `status: FROZEN — awaiting
... commit` until then.  The live runner refuses to run without
FREEZE_COMMIT.txt (written after that commit).

Excluded from the manifest: FREEZE.json itself, FREEZE_COMMIT.txt,
FREEZE_DRAFT.json, the freeze builders, generated sessions/results, HEALTH.json
(post-freeze auth smoke), and __pycache__/.pyc.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "FREEZE.json"
BASIS = HERE.parent / "external_admission_20261024"

EXCLUDE = {
    "FREEZE.json", "FREEZE_COMMIT.txt", "FREEZE_DRAFT.json",
    "build_freeze.py", "build_freeze_draft.py", "HEALTH.json",
    "results.jsonl",
}

TASKS = [
    "2015q-cry-eps",
    "2015q-cry-eps_part2",
    "2017q-cry-almost_xor",
    "2017q-cry-another_xor",
    "2018q-cry-babycrypto",
    "2018q-cry-lowe",
    "2021q-cry-crack_me",
]
SEEDS = [417, 418, 419, 420]
LABELS = ["free/gpt-6-luna", "free/qwen-3.8-max", "free/deepseek-v4.1-flash"]
APINEX_BASE_URL = "https://api.apinex.bond"
TEMPERATURE = 0.2

FB_REJECT = ("EXECUTION_OR_ORACLE_REJECTED: your previous submission did not "
             "run to completion or the oracle did not accept its output. "
             "Revise the program using only the provided artifacts and "
             "resubmit. Return exactly one JSON object with a single \"code\" "
             "string and no prose.")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def group_for(rel):
    if rel.startswith(("PREREGISTRATION", "NOTES", "CRITERION5")):
        return "prereg_and_records"
    if rel.startswith("census_nyu/reference_solvers/"):
        return "criterion5_reference_solvers"
    if rel.startswith("census_nyu/"):
        return "census"
    if rel.startswith("fixtures/rt_transform/"):
        return "prompts"
    if rel.startswith("fixtures/tasks/"):
        return "fixtures_tasks"
    if rel.startswith("fixtures/"):
        return "fixtures_and_transforms"
    if rel.startswith("policies_amend3_draft/"):
        return "policies"
    if rel.startswith("compat_gate/"):
        return "gates"
    if rel.startswith("seed_sweep/"):
        return "seed_sweep"
    if rel.startswith("oracle/"):
        return "oracle"
    if rel in ("run_amend3_sessions.py", "smoke_amend3.py", "smoke_auth_amend3.py",
               "apinex_client.py", "probe_apinex_route.py",
               "HEALTH_ROUTE_PROBE.json", "regrade_amend3_contrast.py"):
        return "harness_and_analysis"
    return "other_frozen_input"


def main():
    files = {}
    for path in sorted(HERE.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if any(part in ("sessions",) for part in path.parts):
            continue
        rel = str(path.relative_to(HERE))
        if rel in EXCLUDE:
            continue
        files[rel] = {"group": group_for(rel), "sha256": sha(path)}
    files["basis::apmix_client.py"] = {
        "group": "basis_read_only_hash_verified",
        "path": "external_admission_20261024/apmix_client.py",
        "sha256": sha(BASIS / "apmix_client.py"),
    }

    outcomes = json.loads(
        (HERE / "census_nyu" / "criterion5_outcomes.json").read_text())
    census = json.loads(
        (HERE / "census_nyu" / "census_nyu_crypto.json").read_text())
    probe = json.loads((HERE / "HEALTH_ROUTE_PROBE.json").read_text())

    payload = {
        "schema": "external-admission-amend3-freeze/2",
        "status": ("FROZEN — awaiting namespace-restricted commit; the live "
                   "runner refuses to run until FREEZE_COMMIT.txt exists"),
        "protocol": "PHASE2-EXTERNAL-ADMISSION-AMEND3-v1",
        "namespace": "external_admission_amend3_20261105",
        "frozen_date": "2026-11-05",
        "authorization": (
            "external_admission_20261024/REPORT.md §6 (expanded external task "
            "source), external_admission_amend1_20261024/REPORT.md §4 (repaired "
            "read boundary + new preregistered amendment), and the paper's §7 "
            "closing requirements; full design in PREREGISTRATION_AMEND3_DRAFT.md"),
        "purpose": (
            "SHA-256 of every prompt, fixture, policy, reference-solve input, "
            "oracle, seed-sweep record, route probe, gate log, F1 script, and "
            "harness input of Amendment 3, committed BEFORE the first "
            "experiment model call. Basis files are hash-verified read-only "
            "references."),
        "conclusion_boundary": (
            "portability + evaluator sensitivity under OUR stress rule only; "
            "never a native benchmark defect; census describes the pinned "
            "2026-10-05 NYU CTF Bench release only; per-label verdicts are "
            "never pooled across labels or with any other cohort; no "
            "benchmark-quality claim"),
        "design": {
            "grid": ("3 labels x 7 tasks x {R0, RT} x seeds [417, 418, 419, "
                     "420] = 168 sessions, n=4 per (label, task, "
                     "representation) cell"),
            "tasks": TASKS,
            "representations": ["R0", "RT"],
            "seeds": SEEDS,
            "labels": LABELS,
            "temperature": TEMPERATURE,
            "max_tokens": 1600,
            "turns": "<=2 (turn-2 identical rejection feedback across representations)",
            "feedback_string": FB_REJECT,
            "execution": ("[python, -I, prog] list argv, shell=False, "
                          "cwd = per-session sandbox holding only the declared "
                          "artifacts, 30s timeout, no extra argv"),
            "oracle": ("exact match stdout.strip() == pinned answer "
                       "(oracle/answers.json; truth material, never prompt content)"),
            "parser": "verbatim P009-family extract_action (JSON object with string 'code')",
            "provider": {
                "route": "APINEX OpenAI-compatible /v1/chat/completions",
                "base_url": APINEX_BASE_URL,
                "labels": LABELS,
                "label_count": len(LABELS),
                "tier": "free (usage cost_tokens 0; no invoice claim)",
                "identity_note": ("provider-attested labels only; no "
                                  "hosted-weight identity claimed"),
                "key_handling": ("APINEX_API_KEY read from the process "
                                 "environment at runtime; never printed, never "
                                 "written to any sp2027 artifact"),
                "phase_ceiling_usd": 5.0,
                "accounting": "0 accounting cost; observed token usage ledgered",
                "two_sided_rule": (
                    "pre-content provider failures: up to 2 recorded "
                    "re-attempts per failed call; exhausted => "
                    "PROVIDER_UNAVAILABLE/TIMEOUT and exclusion from acceptance "
                    "denominators only when no model content was produced; "
                    "post-content failures keep the task-side terminal state; "
                    "auth/billing errors are HARNESS_ERROR and halt the phase; "
                    ">=3 consecutive pre-output session failures => halted"),
            },
            "halt_rule": ">=3 consecutive provider-side pre-output failures => status halted",
            "terminal_enum": [
                "SUCCESS", "ORACLE_FAIL", "TIMEOUT", "AGENT_GIVEUP",
                "MODEL_REFUSAL", "TOOL_FAILURE", "PROVIDER_UNAVAILABLE",
                "HARNESS_ERROR",
            ],
            "artifact_name_policy": "declared basenames, materialized flat",
        },
        "falsifiers": {
            "N": 7, "M": 4, "margin_pp": 10.0,
            "per_label": ("F1_l TRUE iff movement is DEFINED and outside ±10 "
                          "pp on >=4 of 7 tasks; F2_l otherwise; F3_l requires "
                          "every program's output_preserved True; undefined is "
                          "never counted as movement"),
            "cross_label": (">=2 of 3 labels with F1 TRUE and F3 PASSED => "
                            "replicable_across_labels; otherwise report the "
                            "vector (label-sensitive or null); no pooling"),
            "quantity_script": "regrade_amend3_contrast.py (verdicts.per_label and verdicts.cross_label only may be quoted)",
        },
        "pre_freeze_checks": {
            "census": (f"NYU CTF Bench: {census['crypto_challenges_total']} "
                       f"crypto rows, {census['offline_candidates']} offline "
                       "candidates, manifest reconciliation 0-diff both sides"),
            "criterion5": (f"{outcomes['quorum']['qualified']} qualified >= 6 "
                           "required (quorum MET); 1 budget-excluded, 2 "
                           "criterion-5 failures, 6 not reached"),
            "seed_range": ("draft 101–104 found SPENT (info_contract_powered; "
                           "P010 family lists 101–118); registered range "
                           "417–420 verified free; shared across labels by "
                           "design (paired panel)"),
            "decode_equality": "PASS 7/7 (fixtures/decode_equality_log.json)",
            "compat_demonstration": ("amendment-1 frozen prompts: un-repaired "
                                     "v3-boundary arms 0/8; repaired arms 8/8"),
            "compat_freeze_check": ("14/14 new prompts qualify under both "
                                    "registered arms, exit 0 "
                                    "(compat_gate/gate_run_amend3.json)"),
            "prompt_flag_scan": "CLEAN 14/14 (no literal answer in any prompt)",
            "f1_machinery": ("single-label dry run reproduces the corrected "
                             "amended-2 contrasts exactly (F1 FALSE); synthetic "
                             "3-label fixture exercises 2/3 => replicable, "
                             "1/3 => not replicable, F3 failure => exit 3"),
            "route_probe": (
                "pre-freeze non-evidence: 4 APINEX free models 200 at 16 "
                "tokens, cost_tokens 0; selected 3 labels "
                f"{LABELS}; recorded in HEALTH_ROUTE_PROBE.json. The earlier "
                "single-route plan (claude-sonnet-4-6-free via APMIX) was "
                "unavailable pre-freeze (APMIX 404; agentrouter keys 401); no "
                "task-prompt call was made on it."),
            "auth_smoke": ("NOT RUN — post-freeze, non-evidence; separate "
                           "smoke_auth_amend3.py included in this manifest"),
        },
        "files": files,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": payload["status"],
        "files": len(files),
        "labels": LABELS,
        "grid": payload["design"]["grid"],
        "out": str(OUT),
    }, indent=2))


if __name__ == "__main__":
    main()
