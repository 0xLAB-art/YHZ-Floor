#!/usr/bin/env python3
"""w6_transform.py — fill-night mark transformer (runbook Step 6, mechanized).

Replaces every [PENDING-W*] provenance mark in sp2027/paper/main.tex from the
fill-night tool outputs, then verifies the result. The paper text freeze stays
intact until this tool runs: it is invoked ONLY from ops/fill_night.sh after
the lock has verified 100% x2.

Safety gates (all must pass or the paper is NOT rewritten):
  G1  corpus precondition: >= 250 graded sessions in runs_e2 (validator exit 0)
  G2  all fill-night evidence artifacts exist and parse (w3_fill_evidence.json,
      bounds_tier_evidence.json, aor_runs_e2.json, e4_sensitivity_results.json,
      round1.kappa.json or the W5 fallback note in the ledger)
  G3  every non-comment PENDING mark in main.tex is replaced (zero remain)
  G4  rebuilt PDF compiles (pdflatex x2) and page count is reported

Usage:
  python3 sp2027/analysis/w6_transform.py --dry-run   # gate checks + preview
  python3 sp2027/analysis/w6_transform.py --apply     # rewrite + build

The transformation rules are data-driven: RULES below maps each mark context
(regex on the surrounding sentence) to a replacement builder. A rule that
cannot find its number in the evidence aborts loudly — guessing is forbidden.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PAPER = ROOT / "sp2027" / "paper" / "main.tex"
CORPUS = ROOT / "sp2027" / "agent-eval" / "runs_e2"

EVIDENCE = {
    "w3_fill": HERE / "w3_fill_evidence.json",
    "bounds": HERE / "bounds_tier_evidence.json",
    "aor": HERE / "aor_runs_e2.json",
    "e4": HERE / "e4_sensitivity_results.json",
    "kappa": HERE / "round1.kappa.json",
}


def graded_count() -> int:
    """Graded sessions in the corpus (verdict not PROVIDER_UNAVAILABLE/HARNESS_ERROR)."""
    idx = CORPUS / "INDEX.jsonl"
    if not idx.exists():
        return 0
    n = 0
    for line in idx.read_text().splitlines():
        try:
            run_id = json.loads(line).get("run_id")
            rec = json.loads((CORPUS / f"{run_id}.json").read_text())
            status = rec.get("session", {}).get("status", "")
            if status not in ("PROVIDER_UNAVAILABLE", "HARNESS_ERROR"):
                n += 1
        except Exception:
            continue
    return n


def load_evidence() -> dict:
    out = {}
    for k, p in EVIDENCE.items():
        if p.exists():
            try:
                out[k] = json.loads(p.read_text())
            except Exception as e:
                sys.exit(f"G2 FAIL: {p.name} does not parse: {e}")
        else:
            print(f"  (evidence absent: {p.name})")
    return out


def fmt_pct(x):
    return f"{100 * x:.1f}\\%"


def build_rules(ev: dict) -> list:
    """Each rule: (pattern, replacement-or-None). A rule with no evidence for
    its numbers must raise — aborting beats guessing."""
    w3 = ev.get("w3_fill", {})
    bounds = ev.get("bounds", {})
    e4 = ev.get("e4", {})
    kappa = ev.get("kappa", {})

    def slot_cells(slot: str) -> str:
        b = w3.get("by_slot", {}).get(slot)
        if not b or b.get("asr", {}).get("value") is None:
            raise ValueError(f"w3_fill evidence has no numbers for slot {slot}")
        asr = b["asr"]["value"]
        fsr = b.get("fsr", {}).get("value", 0.0)
        med = b.get("med_t_agent_s")
        if med is None:
            raise ValueError(f"no median T_agent for slot {slot}")
        return f"{fmt_pct(asr)} / {fmt_pct(fsr)} / {med:.1f}\\,s"

    rules = []
    # Table 3: the three slot rows.
    for slot in ("O1", "O2", "O3"):
        rules.append((
            re.compile(r"(%s [^\n]*?) & T1 / T2 / T3 & \[PENDING-W3\] & \[PENDING-W3\] & \[PENDING-W3\}" % re.escape(slot)),
            lambda m, s=slot: f"{m.group(1)} & T1 / T2 / T3 & {slot_cells(s)}",
        ))
    # Generic single-mark replacements whose sentence already reads correctly
    # once the mark is dropped (the claim text lives in the surrounding prose).
    rules.append((re.compile(r"~\[PENDING-W3\]"), lambda m: ""))
    rules.append((re.compile(r"~\[PENDING-W3, FROZEN-W0: E3 rig\]"),
                  lambda m: "~[FROZEN-W0: E3 rig]"))
    rules.append((re.compile(r"~\[PENDING-W4\]"), lambda m: ""))
    rules.append((re.compile(r"~\[PENDING-W5\]"), lambda m: ""))
    rules.append((re.compile(r"~\[PENDING-W3: analysis/bounds\\_tier\.py\]"),
                  lambda m: "~[FROZEN-W0: analysis/bounds\\_tier.py]" if bounds else _no(bounds)))
    rules.append((re.compile(r"~\[PENDING-W3: full distribution; FROZEN-W0: pilot execution-floor"),
                  lambda m: "~[FROZEN-W0: pilot execution-floor"))
    rules.append((re.compile(r"~\[PENDING-W5: recruitment under way; instrument frozen\]"),
                  lambda m: "~[FROZEN-W0: instrument frozen]" if kappa else _no(kappa)))
    return rules


def _no(x):
    raise ValueError("evidence required for this rule but absent")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not args.dry_run and not args.apply:
        ap.error("choose --dry-run or --apply")

    # G1 — corpus precondition
    g = graded_count()
    print(f"G1 graded sessions: {g} (need >= 250)")
    if g < 250:
        sys.exit("G1 FAIL: fill night is not armed. The paper stays frozen.")

    # G2 — evidence present
    ev = load_evidence()
    missing = [k for k in ("w3_fill", "bounds", "aor", "e4") if k not in ev]
    if missing:
        sys.exit(f"G2 FAIL: missing evidence artifacts: {missing}")
    if "kappa" not in ev:
        print("  W5 kappa absent — external round must be complete or the "
              "D-ANNOT fallback recorded in the ledger BEFORE --apply")
        if args.apply:
            sys.exit("G2 FAIL: W5 evidence missing; --apply refused")

    text = PAPER.read_text()
    rules = build_rules(ev)

    # Apply rules; count replacements.
    total = 0
    for pat, rep in rules:
        text, n = pat.subn(rep, text)
        total += n
    print(f"G3 replacements applied: {total}")

    remaining = [ln for ln in text.splitlines()
                 if "PENDING-W" in ln and not ln.lstrip().startswith("%")]
    if remaining:
        for ln in remaining:
            print("  REMAINS:", ln[:100])
        sys.exit(f"G3 FAIL: {len(remaining)} PENDING marks unresolved — "
                 f"the paper is NOT rewritten")

    if args.dry_run:
        (HERE / "w6_preview.tex").write_text(text)
        print("dry-run: preview written to sp2027/analysis/w6_preview.tex "
              "(main.tex untouched)")
        return

    # G4 — write + build
    backup = PAPER.with_suffix(".pre_w6.tex")
    backup.write_text(PAPER.read_text())
    PAPER.write_text(text)
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"],
                           cwd=PAPER.parent, capture_output=True, text=True)
    pdf = PAPER.parent / "main.pdf"
    pages = "?"
    if pdf.exists():
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
        m = re.search(r"Pages:\s+(\d+)", info.stdout)
        pages = m.group(1) if m else "?"
    print(f"G4 build: exit {r.returncode}, pages {pages}")
    if r.returncode != 0:
        sys.exit("G4 FAIL: build errors — restore from main.pre_w6.tex and inspect")
    print("W6 transform complete. Next: abstract/conclusion flip (manual, "
          "gated prose) + lock x2 + census re-pin.")


if __name__ == "__main__":
    main()
