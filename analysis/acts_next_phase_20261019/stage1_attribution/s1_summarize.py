#!/usr/bin/env python3
"""Summarise a Stage 1 results file.

Usage:  python3 s1_summarize.py [results.json] [--csv out.csv]

The summary is a *recomputation* over the raw per-case records written by
``s1_runner.py``.  It never re-evaluates anything: it only reads decisions,
expectations and reasons that are already in the results file, so the numbers
printed here are traceable to the raw records.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EVALUATORS = ("digest_only", "signed_digest_only", "signed_context_only", "full", "full_lenient")


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return (0.0, 1.0)
    p = successes / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    half = z * ((p * (1 - p) / total + z * z / (4 * total * total)) ** 0.5) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent / "runs" / "results.json"
    data = json.loads(path.read_text())
    results = data["results"]

    print(f"results file : {path}")
    print(f"case count   : {data['case_count']} (records: {len(results)})")
    print()

    header = f"{'case_id':<42} {'family':<6} " + " ".join(f"{e[:12]:<13}" for e in EVALUATORS) + f"{'expected':<13} {'stage01':<10}"
    print(header)
    print("-" * len(header))
    mismatches = []
    for rec in results:
        dd = rec["decisions_detail"]
        cells = []
        for name in EVALUATORS:
            decision = dd.get(name, {}).get("decision", "-")
            cells.append(f"{decision:<13}")
        exp = rec["expected"]
        exp_strict = exp.get("decision")
        exp_lenient = exp.get("decision_lenient")
        exp_cell = exp_strict if exp_strict == exp_lenient else f"{exp_strict}/{exp_lenient[:4]}"
        s1 = rec.get("stage01") or {}
        s1_cell = s1.get("stage01_final_decision", "N/A")
        print(f"{rec['case_id']:<42} {rec['family']:<6} " + " ".join(cells) + f"{exp_cell:<13} {s1_cell:<10}")
        strict = dd.get("full", {}).get("decision")
        if strict != exp_strict:
            mismatches.append((rec["case_id"], "full", strict, exp_strict))
        lenient = dd.get("full_lenient", {}).get("decision")
        if lenient != exp_lenient:
            mismatches.append((rec["case_id"], "full_lenient", lenient, exp_lenient))
    print()

    if mismatches:
        print("PREREGISTERED-EXPECTATION MISMATCHES (full evaluator):")
        for case, ev, got, want in mismatches:
            print(f"  {case:<42} {ev:<13} got={got} want={want}")
    else:
        print("PREREGISTERED-EXPECTATION MATCHES: full and full_lenient agree with the frozen case table on all cases.")
    print()

    # ---- metrics -----------------------------------------------------------
    def counts(evaluator: str) -> dict[str, int]:
        out = {"success": 0, "reject": 0, "inconclusive": 0}
        key = {"ATTRIBUTED_SUCCESS": "success", "REJECT": "reject", "INCONCLUSIVE": "inconclusive"}
        for rec in results:
            out[key[rec["decisions_detail"][evaluator]["decision"]]] += 1
        return out

    truth_success = [r["case_id"] for r in results if r["expected"].get("crypto_success") is True]
    truth_failure = [r["case_id"] for r in results if r["expected"].get("crypto_success") is False]

    print("=== Decision distribution (n=27) ===")
    for name in EVALUATORS:
        c = counts(name)
        print(f"  {name:<20} ATTRIBUTED_SUCCESS={c['success']:>3}  REJECT={c['reject']:>3}  INCONCLUSIVE={c['inconclusive']:>3}")
    print()

    print("=== False attribution / false rejection (denominator = preregistered ground truth) ===")
    print("    ground truth is 'crypto_success' (the reference predicate), NOT the expected decision,")
    print("    so that a cryptographically TRUE case rejected for a non-crypto reason (A05) is")
    print("    reported separately as a false rejection rather than as a crypto failure.")
    for name in EVALUATORS:
        fp = [r["case_id"] for r in results
              if r["expected"].get("crypto_success") is False
              and r["decisions_detail"][name]["decision"] == "ATTRIBUTED_SUCCESS"]
        fr = [r["case_id"] for r in results
              if r["expected"].get("crypto_success") is True
              and r["decisions_detail"][name]["decision"] in ("REJECT", "INCONCLUSIVE")]
        fp_ci = wilson(len(fp), len(truth_failure))
        fr_ci = wilson(len(fr), len(truth_success))
        print(f"  {name}")
        print(f"     false attribution (promoted a non-success): {len(fp)}/{len(truth_failure)}  Wilson95=[{fp_ci[0]:.3f},{fp_ci[1]:.3f}]  {fp}")
        print(f"     false rejection  (suppressed a success)   : {len(fr)}/{len(truth_success)}  Wilson95=[{fr_ci[0]:.3f},{fr_ci[1]:.3f}]  {fr}")
    print()

    print("=== INCONCLUSIVE vs REJECT separation (omission family B, n=5) ===")
    for name in EVALUATORS:
        cells = []
        for rec in results:
            if rec["family"] != "B":
                continue
            cells.append(f"{rec['case_id'].split('_')[0]}:{rec['decisions_detail'][name]['decision'][:4]}")
        print(f"  {name:<20} {' '.join(cells)}")
    print()

    print("=== Frozen Stage01 pair (frozen: contract_sound_stage01_validator_v2.py + reference verifier) ===")
    s1_cases = [r for r in results if (r.get("stage01") or {}).get("stage01_final_decision")]
    accepted = [r["case_id"] for r in s1_cases if r["stage01"]["stage01_final_decision"] == "ACCEPTED"]
    print(f"  cases with a Stage01 analogue: {len(s1_cases)}/{len(results)}")
    print(f"  Stage01 ACCEPTED: {len(accepted)} -> {accepted}")
    na = [r["case_id"] for r in results if not (r.get("stage01") or {}).get("stage01_final_decision")]
    print(f"  Stage01 N/A (no analogue): {len(na)}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
