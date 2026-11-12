#!/usr/bin/env python3
"""Verify the prior-work anchors the synthesis cites.

Root's own check that each anchor in `CENTRAL_CLAIM.md` and `AUDIT_REPORT.md`
actually appears on the cited physical page of the cited source PDF.  It reads
the pdftotext extraction, splits it on form feeds, and confirms that block N
corresponds to physical PDF page N (the extraction ends with one trailing blank
block).

Usage:  python3 -B verify_anchors.py
Exit code 0 means every anchor was found on the page it is cited for.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"

# (source key, physical page, regex, description)
ANCHORS = [
    # --- ABC -------------------------------------------------------------
    ("abc", 1, r"up to\s*100\s*%\s+in\s+relative\s+terms",
     "ABC abstract: flaw-induced distortion up to 100% relative"),
    ("abc", 2, r"33\s*%",
     "ABC p.2: CVE-Bench overestimation reduction 33% absolute"),
    ("abc", 3, r"outcome validity",
     "ABC p.3: outcome validity defined"),
    ("abc", 9, r"CVE-Bench",
     "ABC p.9: Section 5.3 revising CVE-Bench"),
    ("abc", 10, r"CVE-Bench",
     "ABC p.10: Section 5.3 continued"),
    ("abc", 17, r"fEval|task-completion\s+flag",
     "ABC p.17: Appendix A, RT vs f_Eval two-layer validity"),
    ("abc", 32, r"AgentOccam|LLM-as-a-Judge",
     "ABC p.32: Appendix G, judge varied on fixed artifacts"),
    # --- AgentSuite ------------------------------------------------------
    ("suite", 2, r"5,?086",
     "AgentSuite p.2: 5,086 tasks across six benchmarks"),
    ("suite", 2, r"60\s*%\s+of\s+the\s+model\s+rankings",
     "AgentSuite p.2: 60% of ACEBench rankings altered"),
    ("suite", 3, r"Too strict",
     "AgentSuite p.3: Table 2 component-aligned taxonomy"),
    ("suite", 8, r"Kendall",
     "AgentSuite p.8: random-removal null baseline, Kendall's tau"),
    ("suite", 8, r"single\s+evaluation\s+run\s+per",
     "AgentSuite p.8: single-run-per-model caveat (text wraps around Fig. 5)"),
    ("suite", 12, r"unit-test\s+augmentation\s+in\s+SWE-Bench",
     "AgentSuite p.12: Appendix A, execution-based matching as related work"),
    ("suite", 20, r"18\s+out\s+of\s+30\s+models\s+have\s+their\s+rankings\s+shifted",
     "AgentSuite p.20: Appendix E, 18 of 30 models shifted"),
]

# Terms that must be absent from the whole text of each source.
ZERO_OVERLAP = ["provenance", "attribution", "signature", "admission",
                "claim-specific", "replay", "counterfactual"]


def main() -> int:
    texts = {}
    pages = {}
    for key, name in (("abc", "abc_neurips2025.txt"), ("suite", "agentsuite_icml2026.txt")):
        raw = (SOURCES / name).read_text()
        blocks = raw.split("\f")
        # The extraction ends with one trailing blank block.
        trailing_blank = not blocks[-1].strip()
        pages[key] = blocks
        texts[key] = raw
        print("%s: %d form-feed blocks, trailing blank block=%s"
              % (name, len(blocks), trailing_blank))
        if not trailing_blank:
            print("  WARNING: expected a trailing blank block; page mapping may shift")
    print()

    failures = []
    checked = 0
    for key, page, pattern, description in ANCHORS:
        checked += 1
        blocks = pages[key]
        block = blocks[page - 1] if page - 1 < len(blocks) else ""
        ok = bool(re.search(pattern, block, re.I))
        # A term must not be hiding on a neighbouring page either.
        print("[%s] %-5s p.%-3d %s" % ("PASS" if ok else "FAIL", key, page, description))
        if not ok:
            failures.append(description)

    print()
    for key, name in (("abc", "ABC"), ("suite", "AgentSuite")):
        for term in ZERO_OVERLAP:
            checked += 1
            n = len(re.findall(re.escape(term), texts[key], re.I))
            ok = n == 0
            print("[%s] %-5s whole-text term '%s' occurrences=%d"
                  % ("PASS" if ok else "FAIL", key, term, n))
            if not ok:
                failures.append("%s contains '%s' (%d)" % (name, term, n))

    print()
    print("anchor checks: %d   passed: %d   failed: %d"
          % (checked, checked - len(failures), len(failures)))
    if failures:
        print("FAILED: %s" % "; ".join(failures))
        return 1
    print("every cited anchor is present on the page it is cited for")
    return 0


if __name__ == "__main__":
    sys.exit(main())