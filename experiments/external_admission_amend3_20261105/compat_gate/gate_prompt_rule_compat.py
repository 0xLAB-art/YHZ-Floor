#!/usr/bin/env python3
"""GATE — prompt/rule compatibility pre-check (Amendment 3, DRAFT 2026-11-05).

Closes the exact defect class that produced the amendment-1 degeneracy (0/37
programs admissible; `open:not-readonly-argv1` fired 37/37 only at regrade —
reported in external_admission_amend1_20261024/REPORT.md section 4 and in the
paper's Appendix D.3 'Regrade-degeneracy explanation').

What this gate does, BEFORE any session or model call:

  For every hash-asserted frozen prompt it
    1. re-verifies the prompt sha256 against the freeze manifest,
    2. parses the artifact FILE names from the prompt's `--- FILE: <name> ---`
       blocks (the names the prompt's contract promises the solver,
       "under the same names, in your program's working directory"),
    3. instantiates the MINIMAL contract-reference program — read-only `open`
       of exactly those artifact names in the working directory; imports only
       `sys` (inside every arm's allowed import set by construction),
    4. runs that reference program through EVERY registered arm's policy
       snapshot, and
    5. in `--mode freeze`, asserts the reference program QUALIFIES under EVERY
       registered arm; any reject blocks the freeze.

Modes:
  demonstration  the amendment-1 four-arm panel on the FROZEN amendment-1
                 prompts (un-repaired v3-boundary arms expected to REJECT on
                 all 8; repaired-boundary arms expected to QUALIFY 8/8).  This
                 reproduces the 37/37 defect class at freeze time.
  freeze         the Amendment-3 registered arms on the NEW prompts:
                 declared v4 (policy v3) and stress-repaired (policy legacy);
                 exit 0 only if every prompt passes every arm and every
                 hash/name/materialization check.

A gate failure is a FREEZE-TIME design contradiction — the prompt contract and
the admission rules disagree — and must be repaired (or the rules re-registered)
before the freeze, never discovered post hoc at regrade time.
"""

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path("/mnt/nvme5/ACTS-Attack")
AMEND1 = REPO / "sp2027/research_execution/external_admission_20261024"
AMEND2 = REPO / "sp2027/research_execution/external_admission_amend2_20261029"
AMEND3 = REPO / "sp2027/research_execution/external_admission_amend3_20261105"
OUT_DIR = Path(__file__).resolve().parent

FILE_BLOCK = re.compile(
    r"^--- FILE: (\S+?)(?: \((?:verbatim|base64)\))? ---", re.M)


def load_policy_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_reference_program(artifact_names):
    """The minimal prompt-contract reader: literal read-only opens in the cwd,
    exactly the pattern the freeze-time contract sentence instructs."""
    lines = ["import sys", ""]
    for i, name in enumerate(artifact_names):
        lines.append(f'with open("{name}", "r") as _h{i}:')
        lines.append(f"    _data{i} = _h{i}.read()")
    lines.append("")
    parts = ", ".join(f"_data{i}" for i in range(len(artifact_names)))
    lines.append(f"sys.stdout.write(str(sum(len(_d) for _d in [{parts}])))")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=str(AMEND1))
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--mode", choices=("demonstration", "freeze"),
                        default="demonstration")
    parser.add_argument("--demonstration", action="store_true",
                        help="alias for --mode demonstration")
    args = parser.parse_args()
    mode = "demonstration" if args.demonstration else args.mode
    base = Path(args.base).resolve()
    manifest_path = Path(args.manifest) if args.manifest else base / "PROMPT_HASHES.json"
    out_path = Path(args.out) if args.out else OUT_DIR / (
        "gate_run_log.json" if mode == "demonstration" else "gate_run_amend3.json")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest["instantiated_prompts"]

    if mode == "demonstration":
        v3_mod = load_policy_module(
            AMEND2 / "policies/rule_a_permissive_v3.py", "rule_v3_boundary")
        v4_mod = load_policy_module(
            AMEND2 / "policies/rule_a_permissive_v4.py", "rule_v4_boundary")
        arms = [
            ("a_declared_v3_boundary_v3imports", v3_mod, "v3", True),
            ("b_stress_v3_boundary_legacyimports", v3_mod, "legacy", True),
            ("a2_declared_repaired_boundary_v3imports", v4_mod, "v3", False),
            ("b2_stress_repaired_boundary_legacyimports", v4_mod, "legacy", False),
        ]
        mode_label = "demonstration_on_frozen_amend1_prompts"
    else:
        declared = load_policy_module(
            AMEND2 / "policies/rule_a_permissive_v4.py", "rule_declared_v4")
        stress = load_policy_module(
            base / "policies_amend3_draft/rule_b_stress_legacy_repaired.py",
            "rule_stress_legacy_repaired")
        arms = [
            ("declared_v4_boundary_v3imports", declared, "v3", False),
            ("stress_legacy_repaired_boundary_legacyimports", stress, "legacy", False),
        ]
        mode_label = "freeze_check_on_amend3_prompts"

    records = []
    gate_pass = True
    per_task_artifacts = {}
    for entry in entries:
        prompt_path = base / entry["path"]
        got_sha = sha256_file(prompt_path)
        sha_ok = got_sha == entry["sha256"]
        if not sha_ok:
            gate_pass = False
        text = prompt_path.read_text(encoding="utf-8")
        artifact_names = sorted(set(FILE_BLOCK.findall(text)))
        contract_ok = bool(artifact_names)
        if not contract_ok:
            gate_pass = False
        per_task_artifacts.setdefault(entry["task_id"], set()).add(tuple(artifact_names))
        fixtures_dir = base / "fixtures" / "tasks" / entry["task_id"]
        materialized = {name: (fixtures_dir / name).exists() for name in artifact_names}
        reference = build_reference_program(artifact_names)
        arm_records = []
        for arm_id, module, policy, expect_reject in arms:
            decision = module.qualify_source(reference, policy)
            arm_records.append({
                "arm": arm_id,
                "policy": policy,
                "qualified": decision["qualified"],
                "status": decision["status"],
                "violations": decision["violations"],
                "expected_in_demonstration": "REJECT" if expect_reject else "PASS",
                "matches_expectation": (
                    (not decision["qualified"]) if expect_reject
                    else decision["qualified"]),
            })
            if mode == "freeze" and not decision["qualified"]:
                gate_pass = False
        records.append({
            "task_id": entry["task_id"],
            "representation": entry["representation"],
            "prompt_path": str(prompt_path.relative_to(base))
            if prompt_path.is_relative_to(base) else entry["path"],
            "prompt_sha256_recomputed": got_sha,
            "prompt_sha256_match": sha_ok,
            "prompt_bytes": len(text),
            "artifact_names_from_contract": artifact_names,
            "artifacts_materialized_in_fixture_dir": materialized,
            "contract_reference_source_sha256":
                hashlib.sha256(reference.encode()).hexdigest(),
            "arm_records": arm_records,
        })

    representation_invariance_ok = all(
        len(name_sets) == 1 for name_sets in per_task_artifacts.values())
    if not representation_invariance_ok:
        gate_pass = False
    if not all(all(v for v in r["artifacts_materialized_in_fixture_dir"].values())
               for r in records):
        gate_pass = False
    demonstration_ok = all(
        ar["matches_expectation"] for r in records for ar in r["arm_records"]) \
        if mode == "demonstration" else None

    payload = {
        "schema": "external-admission-amend3-compat-gate/1-draft",
        "gate_version": "2",
        "what_the_gate_asserts": (
            "the minimal prompt-contract reference program (read-only open of "
            "each artifact file the prompt names, cwd-relative) must QUALIFY "
            "under EVERY arm's policy snapshot before the freeze"),
        "mode": mode_label,
        "base": str(base),
        "manifest": str(manifest_path),
        "prompts": len(entries),
        "arms": [a[0] for a in arms],
        "records": records,
        "representation_name_invariance_ok": representation_invariance_ok,
        "all_artifacts_materialized": all(
            all(r["artifacts_materialized_in_fixture_dir"].values())
            for r in records),
        "demonstration_panel_matches_expected": demonstration_ok,
        "all_registered_arms_qualified": all(
            ar["qualified"] for r in records for ar in r["arm_records"]),
        "gate_exit": 0 if gate_pass else 1,
        "notes": [
            "Demonstration mode reproduces, at freeze time, the violation "
            "reason of the amendment-1 regrade rejections "
            "(open:not-readonly-argv1) on the un-repaired arms.",
            "A freeze-mode run must exit 0 on the NEW prompts under the two "
            "registered arms (declared v4 + stress-repaired) before the "
            "freeze is signed.",
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(json.dumps({
        "mode": mode_label,
        "prompts": payload["prompts"],
        "prompt_sha_all_match": all(r["prompt_sha256_match"] for r in records),
        "representation_name_invariance_ok": representation_invariance_ok,
        "artifacts_materialized_all": payload["all_artifacts_materialized"],
        "all_registered_arms_qualified": payload["all_registered_arms_qualified"],
        "panel_matches_expectation": demonstration_ok,
        "per_arm_qualified_counts": {
            arm: sum(1 for r in records for ar in r["arm_records"]
                     if ar["arm"] == arm and ar["qualified"])
            for arm in payload["arms"]
        },
        "out": str(out_path),
    }, indent=2))
    sys.exit(payload["gate_exit"])


if __name__ == "__main__":
    main()
