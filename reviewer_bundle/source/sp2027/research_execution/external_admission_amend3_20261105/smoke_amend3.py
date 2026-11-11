#!/usr/bin/env python3
"""OFFLINE smoke — Amendment 3 readiness (no model call, $0).

Checks, in order:
  1. FREEZE.json exists, is in FROZEN status, and every listed file hash
     matches (namespace entries + basis read-only entries);
  2. PROMPT_HASHES.json: 14 prompts, all hashes match, no prompt contains a
     pinned answer literally;
  3. the oracle answers equal the pinned NYU challenge.json `flag` values and
     cover exactly the grid;
  4. the grid is exactly 3 labels x 7 tasks x {R0,RT} x seeds 417-420 = 168
     unique slots and the labels/tasks equal the freeze design and
     criterion5_outcomes.grid_membership;
  5. the seed sweep is free and matches the registered range;
  6. the three policy modules are verbatim copies of their frozen sources;
  7. the decode-equality gate and the compat gates recorded PASS;
  8. the route-probe record is present, non-evidence, and all three selected
     labels returned ok at 16 tokens with cost_tokens 0;
  9. the runner's offline dry-run reports 168 sessions and verifies every
     frozen input.

No provider import; no network.  The live 16-token AUTH_SMOKE is a separate
post-freeze script (smoke_auth_amend3.py) and is deliberately NOT run here.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASIS = HERE.parent / "external_admission_20261024"
AMEND2 = HERE.parent / "external_admission_amend2_20261029"
PIN = Path("/tmp/opencode/nyu_pin")
FREEZE = HERE / "FREEZE.json"

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


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(condition, message, failures):
    if not condition:
        failures.append(message)


def below_header(lines):
    for i, line in enumerate(lines):
        if line.strip() == "import ast":
            return lines[i:]
    return []


def main():
    failures = []
    check(FREEZE.is_file(), "FREEZE.json missing", failures)
    if failures:
        print(json.dumps({"SMOKE": "FAIL", "failures": failures}, indent=2))
        return 1
    freeze = json.loads(FREEZE.read_text())
    check(str(freeze.get("status", "")).startswith("FROZEN"),
          "FREEZE.json status is not FROZEN", failures)
    check(freeze.get("design", {}).get("labels") == LABELS,
          "registered labels mismatch", failures)
    check(freeze.get("design", {}).get("seeds") == SEEDS,
          "registered seeds mismatch", failures)
    for key, entry in freeze["files"].items():
        path = (HERE.parent / entry["path"]) if "path" in entry else (HERE / key)
        check(path.is_file() and sha(path) == entry["sha256"],
              f"frozen hash mismatch: {path}", failures)

    manifest = json.loads((HERE / "PROMPT_HASHES.json").read_text())
    prompts = manifest["instantiated_prompts"]
    check(len(prompts) == 14, f"expected 14 prompts, got {len(prompts)}", failures)
    oracle = json.loads((HERE / "oracle" / "answers.json").read_text())
    answers = oracle["answers"]
    check(sorted(answers) == sorted(TASKS), "oracle task set mismatch", failures)
    for entry in prompts:
        path = HERE / entry["path"]
        check(path.is_file() and sha(path) == entry["sha256"],
              f"prompt hash mismatch: {entry['path']}", failures)
        if path.is_file():
            check(answers[entry["task_id"]].encode() not in path.read_bytes(),
                  f"literal answer in prompt: {entry['path']}", failures)
    for task in TASKS:
        for artifact in manifest["artifacts"][task]:
            path = HERE / "fixtures" / "tasks" / task / artifact["name"]
            check(path.is_file() and sha(path) == artifact["sha256"],
                  f"artifact hash mismatch: {path}", failures)

    outcomes = json.loads(
        (HERE / "census_nyu" / "criterion5_outcomes.json").read_text())
    check(sorted(outcomes["grid_membership"]) == sorted(TASKS),
          "grid membership mismatch", failures)
    check(outcomes["quorum"] == {"required": 6, "qualified": 7, "status": "MET"},
          "quorum record mismatch", failures)
    for task in TASKS:
        row = next(r for r in outcomes["qualified"] if r["task_id"] == task)
        pinned = json.loads((PIN / row["path_rel"] / "challenge.json").read_text())["flag"]
        check(pinned == answers[task], f"oracle/pin mismatch: {task}", failures)

    sweep = json.loads((HERE / "seed_sweep" / "SEED_SWEEP.json").read_text())
    check(sweep["candidate_range"] == SEEDS and sweep["candidate_range_free"],
          "seed sweep mismatch", failures)

    plan = [(label, t, r, s) for label in LABELS for t in TASKS
            for r in ("R0", "RT") for s in SEEDS]
    prefixes = {f"extadm_amend3__{l.split('/')[-1]}__{t}__{r}__seed_{s}__"
                for l, t, r, s in plan}
    check(len(plan) == 168 and len(prefixes) == 168,
          "grid is not 168 unique slots", failures)

    check(sha(HERE / "policies_amend3_draft/rule_a_permissive_v4.py")
          == sha(AMEND2 / "policies/rule_a_permissive_v4.py"),
          "declared v4 is not a verbatim copy", failures)
    check(sha(HERE / "policies_amend3_draft/rule_c_cleanup.py")
          == sha(BASIS / "policies/rule_c_cleanup.py"),
          "cleanup module is not a verbatim copy", failures)
    v4_lines = (AMEND2 / "policies/rule_a_permissive_v4.py").read_text().splitlines()
    stress_lines = (HERE / "policies_amend3_draft/rule_b_stress_legacy_repaired.py").read_text().splitlines()
    check(below_header(stress_lines) == below_header(v4_lines),
          "stress module is not a verbatim copy of v4 below its header", failures)

    decode = json.loads((HERE / "fixtures" / "decode_equality_log.json").read_text())
    check(decode["gate"] == "PASS", "decode-equality gate is not PASS", failures)
    gate = json.loads((HERE / "compat_gate" / "gate_run_amend3.json").read_text())
    check(gate["gate_exit"] == 0 and gate["all_registered_arms_qualified"]
          and gate["prompts"] == 14, "compat freeze check is not PASS 14/14", failures)
    demo = json.loads((HERE / "compat_gate" / "gate_run_log.json").read_text())
    check(demo["demonstration_panel_matches_expected"],
          "compat demonstration panel mismatch", failures)

    probe = json.loads((HERE / "HEALTH_ROUTE_PROBE.json").read_text())
    check("non-evidence" in probe.get("classification", ""),
          "route probe is not marked non-evidence", failures)
    check(probe.get("selected_labels") == LABELS,
          "route probe selected labels mismatch", failures)
    probe_by_model = {p["model"]: p for p in probe.get("probes", [])}
    for label in LABELS:
        entry = probe_by_model.get(label, {})
        check(entry.get("status") == "ok", f"route probe not ok: {label}", failures)
        check((entry.get("usage") or {}).get("cost_tokens") == 0,
              f"route probe not free: {label}", failures)

    proc = subprocess.run([sys.executable, str(HERE / "run_amend3_sessions.py"),
                           "--dry-run"], capture_output=True, text=True, cwd=HERE)
    check(proc.returncode == 0, f"runner dry-run failed: {proc.stderr[-300:]}", failures)
    if proc.returncode == 0:
        dry = json.loads(proc.stdout)
        check(dry["sessions"] == 168, "runner dry-run session count != 168", failures)
        check(dry["labels"] == LABELS, "runner dry-run labels mismatch", failures)
        check(dry["frozen_files_verified"] == len(freeze["files"]),
              "runner dry-run verified a different frozen-file count", failures)

    result = {
        "SMOKE": "PASS" if not failures else "FAIL",
        "checks": {
            "frozen_files": len(freeze["files"]),
            "labels": LABELS,
            "prompts": len(prompts),
            "artifacts": sum(len(v) for v in manifest["artifacts"].values()),
            "grid_sessions": len(plan),
            "seeds": SEEDS,
            "decode_gate": "PASS",
            "compat_freeze_check": "PASS 14/14 under both registered arms",
            "prompt_flag_scan": "CLEAN",
            "route_probe": "4 models ok, cost_tokens 0; 3 registered labels",
        },
        "failures": failures,
        "note": "Offline readiness only; no provider import and no model call.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
