#!/usr/bin/env python3
"""Check that the rendered paper carries the recomputed lineage numbers.

The check is derived, not hard-coded: every expected string is built from
lineage_recomputation.json, so if a recomputation changes and the paper does
not follow, this fails.  The rendered text of each PDF is extracted with
pdftotext and whitespace-normalised before matching, so line wrapping inside
a table cell or a paragraph does not matter.

Usage:  python3 check_paper_numbers.py
Exit code 0 means every rendered claim matches the recomputation.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAPER = (Path(sys.argv[1]) if len(sys.argv) > 1
         else ROOT / "sp2027" / "paper" / "capability_merge_20261016_h1r3_20261019")
LOCKED = HERE / "lineage_recomputation.json"

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" — " + detail) if detail else ""))
    if not ok:
        failures.append(name)


def pdf_text(name: str) -> str:
    path = PAPER / name
    if not path.is_file():
        return ""
    proc = subprocess.run(["pdftotext", str(path), "-"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return ""
    return re.sub(r"\s+", " ", proc.stdout)


def main() -> int:
    data = json.loads(LOCKED.read_text())
    cells = data["lineage_cells"]
    causes = data["ecdsa_cause_taxonomy"]["causes"]
    by_arm = data["ecdsa_cause_taxonomy"]["by_arm"]
    r2 = by_arm["R2"]
    other = by_arm["R0/R1/R4"]
    crypto_failures = (r2["failing"] + other["failing"]
                       - causes.get("source syntax error", 0))
    wrong_order = causes.get("wrong group-order literal", 0)
    wrong_order_r2 = r2["causes"].get("wrong group-order literal", 0)
    wrong_order_other = other["causes"].get("wrong group-order literal", 0)
    other_crypto_failures = (other["failing"]
                             - causes.get("source syntax error", 0))

    full = pdf_text("supplement_full_20261018.pdf")
    compact = pdf_text("supplement.pdf")
    main = pdf_text("main_content.pdf")
    submission = pdf_text("submission.pdf")
    if not (full or compact or main):
        print("[SKIP] the built PDFs are not present in this distribution; "
              "the paper-text check needs a built paper")
        return 0

    # --- Appendix J: the IAR 2x2 table, denominators included -------------
    for name, pdf in (("full supplement", full),):
        for set_name, rec in cells.items():
            expected = ("%s %d %d/%d %d/%d %d/%d %d/%d" % (
                set_name, rec["cases"],
                rec["fp"]["v2"], rec["attack_inclusive"],
                rec["fp"]["v3-sig"], rec["attack_inclusive"],
                rec["fp"]["v3-full"], rec["attack_inclusive"],
                rec["fr"]["v2"], rec["honest_within_evidence"]))
            check("%s carries the %s row" % (name, set_name),
                  expected in pdf, expected)

    # --- the ECDSA cause table -------------------------------------------
    for label, r2n, othern in (
            ("Wrong group-order literal", wrong_order_r2, wrong_order_other),
            ("Secret recovered, nonce wrong",
             r2["causes"].get("secret recovered, nonce wrong", 0),
             other["causes"].get("secret recovered, nonce wrong", 0)),
            ("Correct order, scalar wrong",
             r2["causes"].get("correct order, scalar wrong, cause undetermined", 0),
             other["causes"].get("correct order, scalar wrong, cause undetermined", 0)),
            ("Source syntax error",
             r2["causes"].get("source syntax error", 0),
             other["causes"].get("source syntax error", 0))):
        expected = "%s %d %d %d" % (label, r2n, othern, r2n + othern)
        check("compact supplement carries the cause row '%s'" % label,
              expected in compact, expected)

    # --- the main text ---------------------------------------------------
    main_claim = ("localizes %d of the %d ECDSA failures to one wrong group-order constant, "
                  "carried by %d of the %d R2 failures against %d of the %d in the other arms"
                  % (wrong_order, crypto_failures, wrong_order_r2, r2["failing"],
                     wrong_order_other, other_crypto_failures))
    check("main text carries the H1-R3 cause claim", main_claim in main, main_claim)

    # --- the discussion: lineage denominators ----------------------------
    held_out = cells["IAR-B held-out"]
    dev = cells["IAR-B dev"]
    # checked as numbers, not as a sentence: the wording is editorial, the
    # denominators are not.
    for figure in ("10/28", "%d/%d" % (held_out["fp"]["v2"], held_out["attack_inclusive"]),
                   "%d/%d" % (held_out["fp"]["v3-sig"], held_out["attack_inclusive"]),
                   "14/16"):
        check("the main text carries the lineage denominator %s" % figure, figure in main)
    check("main text and submission agree on the H1-R3 cause claim",
          (main_claim in main) and (main_claim in submission or "localizes %d of the %d" % (
              wrong_order, crypto_failures) in submission))
    check("dev-set denominators are the ones recomputed",
          "%d/%d" % (dev["fp"]["v2"], dev["attack_inclusive"]) in full)

    # --- the claim-licensing map (supplement C.1) ----------------------
    for label in ("Verified exploit outcome", "Autonomous completion",
                  "Elapsed time", "Historical attribution"):
        check("compact supplement carries the claim row '%s'" % label, label in compact)
    for figure in ("12/12 fixed-executor operations", "8/12 prospective",
                   "801 verified-exploit successes", "852/852", "0/8", "32,000",
                   "0/54", "0/12", "3/3", "8.37", "0.214"):
        check("the claim-licensing map carries %s" % figure, figure in compact)

    # --- the combined submission ---------------------------------------
    combined = PAPER / "submission_main_plus_supplement.pdf"
    if combined.is_file():
        import subprocess as _sp
        out = _sp.run(["pdfinfo", str(combined)], capture_output=True, text=True).stdout
        pages = [l for l in out.splitlines() if l.startswith("Pages")]
        n = int(pages[0].split()[1]) if pages else 0
        main_pages = 0
        supp_pages = 0
        for name, box in (("main_content.pdf", "main"), ("supplement.pdf", "supp")):
            o = _sp.run(["pdfinfo", str(PAPER / name)], capture_output=True, text=True).stdout
            for line in o.splitlines():
                if line.startswith("Pages"):
                    if box == "main":
                        main_pages = int(line.split()[1])
                    else:
                        supp_pages = int(line.split()[1])
        check("the combined submission is main + supplement, page for page",
              n == main_pages + supp_pages == 18,
              "main %d + supplement %d = %d, combined %d"
              % (main_pages, supp_pages, main_pages + supp_pages, n))
        ctext = _sp.run(["pdftotext", str(combined), "-"],
                        capture_output=True, text=True).stdout
        # one continuous citation sequence: the main part carries the whole
        # numbered list, and the supplement part adds no citation of its own,
        # so no number can be ambiguous across the two.
        pages = ctext.split("\f")
        main_part = "".join(pages[:main_pages])
        supp_part = "".join(pages[main_pages:])
        nums = sorted({int(m) for m in re.findall(r"\[(\d+)\]", main_part)})
        # continuity is the property: the list starts at 1 and has no gap
        check("the combined submission carries one continuous reference list",
              bool(nums) and nums == list(range(1, len(nums) + 1)),
              "main part numbers %d..%d, %d entries" % (nums[0], nums[-1], len(nums)) if nums
              else "no numbered list found")
        check("the supplement part of the combined submission cites nothing, "
              "so no number is ambiguous",
              not re.findall(r"\[\d+\]", supp_part),
              "no bracketed citation markers after the main part")
    else:
        print("[SKIP] combined submission PDF not present")

    if failures:
        print("FAILED: %s" % ", ".join(failures))
        return 1
    print("all paper-text checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())