"""Check citation completeness and order for each built document.

For every document we build, collect the keys cited by the sources it
includes and the keys defined by the bibliography it includes, and report
keys that are cited but never defined.  This is the reviewer's "verify
bibliography completeness and citation order" check.

Usage:  python3 check_citations.py <paper-dir>
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPER = (Path(sys.argv[1]) if len(sys.argv) > 1
         else ROOT / "sp2027" / "paper" / "capability_revision_20261020")

CITE = re.compile(r"\\cite\{([^}]+)\}")
BIB = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}")


def cites_in(paths):
    keys = set()
    for p in paths:
        if not p.is_file():
            continue
        for m in CITE.finditer(p.read_text(errors="replace")):
            for k in m.group(1).split(","):
                k = k.strip().split("~")[0].split(":")[0]
                if k:
                    keys.add(k)
    return keys


def bibs_in(paths):
    keys = set()
    for p in paths:
        if not p.is_file():
            continue
        for m in BIB.finditer(p.read_text(errors="replace")):
            keys.add(m.group(1))
    return keys


def first_citation_numbers(aux_path):
    if not aux_path.is_file():
        return None
    aux = aux_path.read_text()
    ordered = list(dict.fromkeys(
        key for group in re.findall(r"\\citation\{([^}]+)\}", aux)
        for key in group.split(",")))
    numbers = {key: int(number) for key, number in
               re.findall(r"\\bibcite\{([^}]+)\}\{(\d+)\}", aux)}
    return [numbers.get(key) for key in ordered]


# main_content.tex includes the appendix only under \ifdefined\IncludeSupportingAppendices.
# A document built without that flag must not be charged with the appendix's citations.
CONDITIONAL = ("appendix_content", "submission_appendix_content")


def inputs_of(tex):
    """All files a tex includes, transitively, with the bibliography it uses."""
    seen, files, bibs = set(), set(), set()

    def walk(path, depth=0):
        if depth > 6 or not path.is_file() or path in seen:
            return
        seen.add(path)
        text = path.read_text(errors="replace")
        if "\\bibitem" in text:
            bibs.add(path)
        for m in re.finditer(r"\\input\{([^}]+)\}", text):
            if any(c in m.group(1) for c in CONDITIONAL):
                continue
            target = path.parent / (m.group(1) + ".tex")
            if not target.is_file():
                target = PAPER / (m.group(1) + ".tex")
            walk(target, depth + 1)

    walk(tex)
    files = seen
    return files, bibs


def main():
    documents = {
        "main_content": PAPER / "main_content.tex",
        "supplement": PAPER / "supplement.tex",
        "supplement_merged": PAPER / "supplement_merged.tex",
        "submission (combined)": PAPER / "submission_main_plus_supplement.tex",
    }
    bad = 0
    unchecked = 0
    for name, tex in documents.items():
        if not tex.is_file():
            print("  %-22s (no such build file)" % name)
            continue
        files, bibs = inputs_of(tex)
        cited = cites_in(files)
        defined = bibs_in(bibs)
        missing = sorted(cited - defined)
        uncited = sorted(defined - cited)
        print("  %-22s sources=%2d  bibs=%d  cited=%2d  defined=%2d"
              % (name, len(files), len(bibs), len(cited), len(defined)))
        if missing:
            print("      UNDEFINED CITATIONS: %s" % ", ".join(missing))
            bad += len(missing)
        if uncited:
            print("      defined but never cited: %s" % ", ".join(uncited))
        numbers = first_citation_numbers(tex.with_suffix(".aux"))
        if numbers is None:
            print("      first-citation numbering: NOT CHECKED (build the document)")
            unchecked += 1
        elif len(numbers) != len(cited):
            print("      source/compiled citation census: FAIL")
            bad += 1
        elif numbers == list(range(1, len(numbers) + 1)):
            print("      first-citation numbering: PASS (%d entries)" % len(numbers))
        else:
            print("      first-citation numbering: FAIL %r" % numbers)
            bad += 1
    print()
    print("citation check: %s" % ("FAIL" if bad else "PARTIAL" if unchecked else "PASS"))
    return 1 if bad else 2 if unchecked else 0


if __name__ == "__main__":
    raise SystemExit(main())
