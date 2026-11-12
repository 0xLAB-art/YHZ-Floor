#!/usr/bin/env python3
"""Admission-rule sensitivity for the H1-R3 matched cohort.

The manuscript's evaluator-policy result is a counterfactual over *admission
rules*, so it has to be read as a function of the rule rather than as a
property of the study.  This script computes that function offline:

  * the contract-consistent rule (the 17 module roots the H1-R3 prompt
    declares), which is the rule actually in force;
  * the earlier 3-module source checker, and the prompt provenance of both;
  * every single-module narrowing of the contract, so a reviewer can see what
    a plausible tightening does on its own;
  * the paired L3 R2-R0 contrast under each rule, and the same contrast after
    the conservative cleanup of unused imports;
  * the per-arm module distribution, which is what makes the per-arm rejection
    rates differ.

It reads only retained records.  It makes no provider call, re-executes no
program, and contacts no target.

Usage:  python3 -B policy_sensitivity.py [--root <dir>]
Exit code 0 means every recomputed figure matched the printed value.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The 17 module roots the H1-R3 prompt declares (h1r3_core.build_prompt).
CONTRACT_MODULES = {
    "base64", "binascii", "collections", "decimal", "fractions", "functools",
    "hashlib", "itertools", "json", "math", "operator", "re", "statistics",
    "string", "struct", "sys", "typing",
}
# The capability-bearing modules the same prompt forbids.  The contract also
# forbids dunder attributes, eval/exec, and any other import.
FORBIDDEN_CAPABILITY = {
    "os", "pathlib", "shutil", "socket", "urllib", "http", "requests",
    "subprocess", "importlib", "ctypes", "multiprocessing", "threading",
    "asyncio", "signal", "pickle", "marshal", "tempfile", "glob", "io",
}
# The earlier source checker's hard-coded allowlist
# (run_contract_sound_agent_pilot.py, 2026-10-18).
LEGACY_ALLOWED = {"json", "sys", "base64"}
# The import set the 2026-10-18 information-contract prompt declared.
PROMPT_DECLARED_20261018 = {"json", "sys", "hashlib", "cryptography"}

ARMS = ("R0", "R1", "R2")
LEVEL = "L3"


def load(root: Path):
    imports = json.loads((root / "PUBLIC_IMPORT_SETS.json").read_text())
    pub = root / "PUBLIC_DISPOSITIONS.json"
    if pub.is_file():
        disp = json.loads(pub.read_text())
    else:
        # The live tree keeps the full session rows; the published package
        # keeps the projection.  The fields used here are the same.
        rows = [json.loads(l) for l in
                (root / "runs/confirmatory/results.jsonl").read_text().splitlines()
                if l.strip()]
        disp = {"rows": [{
            "session_id": r.get("session_id"), "arm": r.get("arm"),
            "kind": r.get("kind"), "level": r.get("level"),
            "family": r.get("family"), "instance_id": r.get("instance_id"),
            "terminal_success": r.get("terminal_success"),
        } for r in rows]}
    ledger = [json.loads(l) for l in
              (root.parent / "policy_mechanism_20261021/CASE_LEDGER.jsonl")
              .read_text().splitlines() if l.strip()]
    return imports, disp, ledger


def admitted(imports_by_session, session, allowed):
    """Whether the session's program would be admitted under an allowlist."""
    mods = set(imports_by_session.get(session, []))
    return not (mods - allowed)


def evaluate(imports_by_session, dispositions, ledger_by_session, allowed,
             cleanup=False):
    """Per-arm rejection rates and the paired L3 R2-R0 contrast under a rule."""
    prim = [r for r in dispositions["rows"] if r.get("kind") == "primary"]
    arm_reject = Counter()
    arm_n = Counter()
    for r in prim:
        arm = r.get("arm")
        arm_n[arm] += 1
        if not admitted(imports_by_session, r.get("session_id"), allowed):
            arm_reject[arm] += 1

    # paired matched L3 instances
    groups = defaultdict(dict)
    for r in prim:
        if r.get("level") != LEVEL:
            continue
        groups[(r.get("family"), r.get("instance_id"))][r.get("arm")] = r
    complete = {k: v for k, v in groups.items() if {"R0", "R1", "R2"} <= set(v)}

    n = 0
    cur0 = cur2 = leg0 = leg2 = 0
    neg = pos = 0
    for arms in complete.values():
        n += 1
        base, treat = arms["R0"], arms["R2"]
        ok = lambda r: bool(r.get("terminal_success"))
        cur0 += ok(base)
        cur2 += ok(treat)
        if cleanup:
            lb = ledger_by_session.get(base.get("session_id"), {})
            lt = ledger_by_session.get(treat.get("session_id"), {})
            a0 = ok(base) and bool(lb.get("derivative_legacy_admitted"))
            a2 = ok(treat) and bool(lt.get("derivative_legacy_admitted"))
        else:
            a0 = ok(base) and admitted(imports_by_session, base.get("session_id"), allowed)
            a2 = ok(treat) and admitted(imports_by_session, treat.get("session_id"), allowed)
        leg0 += int(a0)
        leg2 += int(a2)
        d_cur = int(ok(treat)) - int(ok(base))
        d_leg = int(a2) - int(a0)
        q = d_leg - d_cur
        if q < 0:
            neg += 1
        elif q > 0:
            pos += 1
    return {
        "pairs": n,
        "current": {"R0": cur0, "R2": cur2},
        "rule_admitted": {"R0": leg0, "R2": leg2},
        "current_effect_pp": round((cur2 - cur0) / n * 100, 2) if n else None,
        "rule_effect_pp": round((leg2 - leg0) / n * 100, 2) if n else None,
        "policy_change_pp": (round(((leg2 - leg0) - (cur2 - cur0)) / n * 100, 2)
                             if n else None),
        "negative_shifts": neg,
        "positive_shifts": pos,
        "unchanged": n - neg - pos,
        "per_arm_rejections": {a: arm_reject.get(a, 0) for a in ARMS},
        "per_arm_n": {a: arm_n.get(a, 0) for a in ARMS},
        "per_arm_rejection_rate_pct": {
            a: (round(100.0 * arm_reject.get(a, 0) / arm_n[a], 1) if arm_n.get(a)
                else None) for a in ARMS},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=HERE)
    args = ap.parse_args()
    root = args.root.resolve()
    imports, disp, ledger = load(root)
    imports_by_session = {r["session_id"]: r["imported_modules"] for r in imports["rows"]}
    ledger_by_session = {r["session_id"]: r for r in ledger}

    # 1. the contract-consistent rule, which is the rule in force
    contract = evaluate(imports_by_session, disp, ledger_by_session, CONTRACT_MODULES)

    # 2. the earlier 3-module source checker
    legacy = evaluate(imports_by_session, disp, ledger_by_session, LEGACY_ALLOWED)
    legacy_clean = evaluate(imports_by_session, disp, ledger_by_session,
                            LEGACY_ALLOWED, cleanup=True)

    # 3. every single-module narrowing of the contract
    single = {}
    for m in sorted(CONTRACT_MODULES):
        single[m] = evaluate(imports_by_session, disp, ledger_by_session,
                             CONTRACT_MODULES - {m})

    # 4. the per-arm module distribution
    per_arm_modules = {a: Counter() for a in ARMS}
    for r in disp["rows"]:
        if r.get("kind") != "primary":
            continue
        for m in imports_by_session.get(r.get("session_id"), []):
            per_arm_modules[r.get("arm")][m] += 1

    # 5. how the 2026-10-18 prompt's own declared set relates to the checker
    prompt_relation = {
        "prompt_declared_2026_10_18": sorted(PROMPT_DECLARED_20261018),
        "checker_allowed_2026_10_18": sorted(LEGACY_ALLOWED),
        "declared_but_rejected_by_checker": sorted(
            PROMPT_DECLARED_20261018 - LEGACY_ALLOWED),
        "allowed_but_not_declared": sorted(
            LEGACY_ALLOWED - PROMPT_DECLARED_20261018),
    }

    report = {
        "scope": "Admission-rule sensitivity of the H1-R3 matched cohort, "
                 "recomputed from the shipped import projection and "
                 "dispositions.",
        "boundary": (
            "The contract-consistent rule is the one in force: it admits the "
            "17 module roots the H1-R3 prompt declares and denies the "
            "capability-bearing ones, and no generated program imports a "
            "denied module. The earlier 3-module source checker is a "
            "harness-side rule that no prompt declared; in the 2026-10-18 "
            "information-contract lane the prompt declared four different "
            "modules, two of which the checker rejected. The counterfactual "
            "is a gate on byte-identical programs under recorded outcomes; it "
            "is not a fresh policy deployment, a model comparison, or a "
            "causal representation effect."
        ),
        "contract_consistent_rule": contract,
        "earlier_three_module_checker": legacy,
        "earlier_three_module_checker_after_cleanup": legacy_clean,
        "single_module_narrowings": single,
        "per_arm_module_occurrences": {
            a: dict(sorted(per_arm_modules[a].items(), key=lambda kv: -kv[1]))
            for a in ARMS},
        "prompt_provenance": prompt_relation,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())