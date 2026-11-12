#!/usr/bin/env python3
"""Build FREEZE.json — Amendment 4 (frontier label panel, 2026-11-06).

Hashes every frozen input of the Amendment-4 bundle plus the read-only basis
files (the frozen agentrouter transport adapters and the Amendment-3 runner
this protocol inherits from), records the design (3 frontier labels, dual
codings, CRASH class, token ceiling) and the executed pre-freeze gates, and
writes FREEZE.json.  The namespace-restricted freeze commit is the
registration act.  The live runner refuses to run without FREEZE_COMMIT.txt.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "FREEZE.json"
BASIS = HERE.parent / "external_admission_amend3_20261105"
ADAPTERS = HERE.parent / "provider_adapter_agentrouter_p017.py"

EXCLUDE = {
    "FREEZE.json", "FREEZE_COMMIT.txt", "FREEZE_DRAFT.json",
    "build_freeze.py", "HEALTH.json", "results.jsonl",
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
SEEDS = [421, 422, 423, 424]
LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]
SUBSTITUTE_ORDER = ["gpt-6.1-sol", "gpt-5.6-sol", "gpt-6-astra"]
BASE_URL = "https://agentrouter.org"
TEMPERATURE = 0.2
MAX_TOKENS = 4200

FB_REJECT = ("EXECUTION_OR_ORACLE_REJECTED: your previous submission did not "
             "run to completion or the oracle did not accept its output. "
             "Revise the program using only the provided artifacts and "
             "resubmit. Return exactly one JSON object with a single \"code\" "
             "string and no prose.")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def group_for(rel):
    if rel.startswith("PREREGISTRATION"):
        return "prereg_and_records"
    if rel.startswith("census_nyu/"):
        return "census"
    if rel.startswith("fixtures/rt_transform/"):
        return "prompts"
    if rel.startswith("fixtures/tasks/"):
        return "fixtures_tasks"
    if rel.startswith("fixtures/"):
        return "fixtures_and_transforms"
    if rel.startswith("policies_amend4/"):
        return "policies"
    if rel.startswith("compat_gate/"):
        return "gates"
    if rel.startswith("seed_sweep"):
        return "seed_sweep"
    if rel.startswith("oracle/"):
        return "oracle"
    if rel in ("run_amend4_sessions.py", "smoke_auth_amend4.py",
               "agentrouter_client.py", "PROMPT_HASHES.json"):
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
    files["basis::provider_adapter_agentrouter_p017.py"] = {
        "group": "basis_read_only_hash_verified",
        "path": "external_admission_amend3_20261105/../provider_adapter_agentrouter_p017.py",
        "sha256": sha(ADAPTERS),
    }
    files["basis::run_amend3_sessions.py"] = {
        "group": "basis_read_only_hash_verified",
        "path": "external_admission_amend3_20261105/run_amend3_sessions.py",
        "sha256": sha(BASIS / "run_amend3_sessions.py"),
    }
    files["basis::oracle_answers_amend3.json"] = {
        "group": "basis_read_only_hash_verified",
        "path": "external_admission_amend3_20261105/oracle/answers.json",
        "sha256": sha(BASIS / "oracle" / "answers.json"),
    }

    outcomes = json.loads(
        (HERE / "census_nyu" / "criterion5_outcomes.json").read_text())
    census = json.loads(
        (HERE / "census_nyu" / "census_nyu_crypto.json").read_text())

    # prompt flag scan: no pinned-answer bytes in any prompt (14 files)
    answers = json.loads((HERE / "oracle" / "answers.json").read_text())["answers"]
    flag_hits = []
    for e in json.loads((HERE / "PROMPT_HASHES.json").read_text())["instantiated_prompts"]:
        text = (HERE / e["path"]).read_text()
        if answers[e["task_id"]].encode() in text.encode():
            flag_hits.append(e["path"])

    payload = {
        "schema": "external-admission-amend4-freeze/1",
        "status": ("FROZEN — awaiting namespace-restricted commit; the live "
                   "runner refuses to run until FREEZE_COMMIT.txt exists"),
        "protocol": "PHASE2-EXTERNAL-ADMISSION-AMEND4-FRONTIER-v1",
        "namespace": "external_admission_amend4_frontier_20261106",
        "frozen_date": "2026-11-06",
        "authorization": (
            "Author decision 2026-11-06 (option B): the registered 4-of-7 "
            "portability bar receives its first full test on the paper's own "
            "frontier GPT-family labels; Amendment-3's record stands unchanged; "
            "full design in PREREGISTRATION_AMEND4_FRONTIER.md"),
        "purpose": (
            "SHA-256 of every prompt, fixture, policy, oracle, census, "
            "seed-sweep record, gate, and harness input of Amendment 4, "
            "committed BEFORE the first experiment model call. Basis files "
            "are hash-verified read-only references."),
        "conclusion_boundary": (
            "portability + evaluator sensitivity under OUR stress rule only; "
            "never a native benchmark defect; census describes the pinned "
            "2026-10-05 NYU CTF Bench release only; per-label verdicts are "
            "never pooled across labels, codings, or with any other cohort; "
            "no benchmark-quality claim"),
        "design": {
            "grid": ("3 labels x 7 tasks x {R0, RT} x seeds [421, 422, 423, "
                     "424] = 168 sessions, n=4 per (label, task, "
                     "representation) cell"),
            "tasks": TASKS,
            "representations": ["R0", "RT"],
            "seeds": SEEDS,
            "labels": LABELS,
            "temperature": TEMPERATURE,
            "temperature_by_label": {"all": "route default (temperature field omitted for every label; the route rejects explicit 0.2 — pre-first-call amendments 1-2)"},
            "max_tokens": MAX_TOKENS,
            "turns": "<=2 (turn-2 identical rejection feedback across representations)",
            "feedback_string": FB_REJECT,
            "execution": ("[python, -I, prog] list argv, shell=False, "
                          "cwd = per-session sandbox holding only the declared "
                          "artifacts, 30s timeout, no extra argv"),
            "oracle": {
                "C1_primary": ("stdout.strip() == pinned answer, rc==0 "
                               "(registered; unchanged from Amendment 3)"),
                "C2_second_admissible_normalization": (
                    "first flag-shaped token (flag\\{[ -~]*?\\}) in stdout == "
                    "pinned answer, rc==0 — registered before the first call; "
                    "acceptance/SUCCESS is C1; C2 reported side by side "
                    "(P024b both-codings discipline)"),
            },
            "parser": "verbatim P009-family extract_action (JSON object with string 'code')",
            "provider": {
                "route": "agentrouter gateway, Anthropic-messages /v1/messages",
                "base_url": BASE_URL,
                "labels": LABELS,
                "label_count": len(LABELS),
                "identity_note": ("provider-attested labels only; no "
                                  "hosted-weight identity claimed; "
                                  "claude-cli User-Agent per the frozen "
                                  "adapters (basis hash-verified)"),
                "key_handling": ("AGENTROUTER_API_KEY read from the process "
                                 "environment at runtime; never printed, never "
                                 "written to any sp2027 artifact"),
                "substitution_order": SUBSTITUTE_ORDER,
                "output_token_ceiling": 2_500_000,
                "output_token_checkpoint": 2_000_000,
                "accounting": ("token counts ledgered per call; USD "
                               "reconciled at settlement from the gateway's "
                               "invoicing"),
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
                "SUCCESS", "CRASH", "ORACLE_FAIL", "TIMEOUT", "AGENT_GIVEUP",
                "MODEL_REFUSAL", "TOOL_FAILURE", "PROVIDER_UNAVAILABLE",
                "HARNESS_ERROR",
            ],
            "crash_class": ("CRASH = the FINAL submitted program exited "
                            "non-zero (registered up front per the Amendment-3 "
                            "decomposition finding: 103 terminal crashes hid "
                            "inside ORACLE_FAIL)"),
            "artifact_name_policy": "declared basenames, materialized flat",
        },
        "falsifiers": {
            "N": 7, "M": 4, "margin_pp": 10.0,
            "per_label": ("F1_l TRUE iff movement is DEFINED and outside ±10 "
                          "pp on >=4 of 7 tasks, computed under C1 and under "
                          "C2 separately; F2_l otherwise; F3_l requires every "
                          "program's output_preserved True; undefined is "
                          "never counted as movement"),
            "cross_label": (">=2 of 3 labels with F1 TRUE and F3 PASSED => "
                            "replicable_across_labels; otherwise report the "
                            "vector; no pooling"),
            "quantity_script": "regrade_amend4_contrast.py (both codings)",
        },
        "pre_freeze_checks": {
            "census": (f"NYU CTF Bench: {census['crypto_challenges_total']} "
                       f"crypto rows, {census['offline_candidates']} offline "
                       "candidates (copied byte-identical from Amendment 3)"),
            "criterion5": (f"{outcomes['quorum']['qualified']} qualified >= 6 "
                           "required (quorum MET); same grid membership"),
            "seed_range": ("[421, 422, 423, 424] verified free by the sweep "
                           "over every research_execution results.jsonl seed "
                           "field and seeds receipt (seed_sweep_SEED_SWEEP_"
                           "json; P022's 19-digit CSPRNG seeds are a "
                           "different magnitude class)"),
            "decode_equality": "PASS (fixtures/decode_equality_log.json, "
                               "copied byte-identical from Amendment 3)",
            "prompt_identity": ("the 14 prompt files and 10 artifacts are "
                                "byte-identical to Amendment-3's frozen "
                                "inputs (PROMPT_HASHES.json re-verified this "
                                "namespace); their admission compatibility "
                                "was exercised by the Amendment-3 run itself "
                                "(261/282 declared-qualified, 0/37-style "
                                "degeneracy absent)"),
            "prompt_flag_scan": (f"{'CLEAN 14/14' if not flag_hits else 'HITS: ' + str(flag_hits)}"
                                 " (no literal pinned answer in any prompt)"),
            "compat_gate": ("demonstration mode on the frozen Amend-1 prompts "
                            "reproduced the expected panel (gate_exit 0); "
                            "the Amend-4 prompts are the Amend-3 prompts "
                            "already compat-exercised end to end"),
        },
        "post_freeze_non_evidence": {
            "auth_smoke": ("one AUTH_SMOKE per label before the run "
                           "(HEALTH.json; evidence=false)"),
            "fingerprint_audit": ("post-run per-label echo check; a drifting "
                                  "cohort is withdrawn to same-label"),
        },
        "excluded_from_manifest": sorted(EXCLUDE),
        "files": files,
    }
    OUT.write_text(json.dumps(payload, indent=1))
    print(f"wrote {OUT} with {len(files)} frozen files")
    print("prompt_flag_scan:", "CLEAN" if not flag_hits else f"HITS {flag_hits}")


if __name__ == "__main__":
    main()
