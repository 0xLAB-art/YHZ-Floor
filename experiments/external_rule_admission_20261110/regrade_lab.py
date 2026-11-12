#!/usr/bin/env python3
"""Regrade Lab — third-party executability for the external-rule regrade wave.

One command re-derives any registered or external-provenance oracle count on the
frozen records. Ships in the anonymized reviewer bundle; any reader becomes the
external evaluator by running it.

  python3 regrade_lab.py                       # both records, every declared rule
  python3 regrade_lab.py --record A --rule E3_cybench_substring

No model calls, no network. LOCKED amend3/amend5 dirs are read-only.
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_external_rule_regrade import (  # noqa: E402
    EXTERNAL_RULES,
    INPUTS,
    RULE_ORDER,
    regrade_record,
    write_freeze,
)

RECORDS = {
    "A": ("R_A_amend5_transport", INPUTS["R_A_answers"], INPUTS["R_A_regrade"], INPUTS["R_A_results"]),
    "B": ("R_B_amend3_nyu", INPUTS["R_B_answers"], INPUTS["R_B_regrade"], INPUTS["R_B_results"]),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--record", choices=["A", "B", "both"], default="both")
    ap.add_argument("--rule", choices=RULE_ORDER, default=None,
                    help="print a single rule's count; default: every declared rule")
    args = ap.parse_args()

    write_freeze()
    keys = ["A", "B"] if args.record == "both" else [args.record]
    rules = [args.rule] if args.rule else RULE_ORDER

    for key in keys:
        tag, answers, regrade, results = RECORDS[key]
        rec = regrade_record(tag, answers, regrade, results)
        total = rec["programs_total"]
        print(f"\n== Record {key} ({tag}) — {total} frozen programs, "
              f"{rec['sessions_total']} sessions ==")
        for rule in rules:
            n = rec["program_level_counts"][rule]
            if rule in EXTERNAL_RULES:
                provenance = "external-published"
            elif rule.startswith(("E1c", "E2c")):
                provenance = "external-secondary"
            else:
                provenance = "authorial"
            base = rec["program_level_counts"]["C1_whole_equals"]
            delta = "" if rule == "C1_whole_equals" else f"  (Δ {n - base:+d} vs C1)"
            print(f"  {rule:<34} {n:>3}/{total}   [{provenance}]{delta}")
    print("\nPre-registration: PREREGISTRATION_EXTERNAL_RULE_REGRADE.md · "
          "Finding: FINDING_EXTERNAL_RULE_REGRADE.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
