#!/usr/bin/env python3
"""
build_second_audit_packet.py — W5/E1 blind re-audit packet generator.

The paper's frozen commitment (sec:e1 Method + the [PENDING-W5] marks):
"A second auditor independently re-derives all 54 judgment cells (six
benchmarks x nine fields) blind to the first pass for agreement."

This tool builds that packet so the second auditor never sees a first-pass
judgment before committing their own:

  - cells = 6 benchmarks x 9 fields (F1..F9 exactly as defined in the
    paper's rubric subsection — not the 10-row RUBRIC.md working list),
  - cell order: deterministic shuffle (seed from --seed, default 20261005,
    recorded in the packet manifest) so "blind" is also order-blind,
  - each cell card carries ONLY: benchmark name, field id + the rubric's
    definition text, the evidence SOURCES to inspect (paper + repo + pinned
    commit from the first-pass worksheet's artifact snapshot, and the
    evidence/ directory paths) — never the first-pass value,
  - emitted: annotators/second_audit/packet.json (machine), cells/*.md
    (human cards), INSTRUCTIONS.md, record_answers.py (neutral entry that
    stores answers and only then reveals+scores against the first pass).

NOTHING here judges: the tool packages evidence sources; judgments are
human. Agreement statistics (Fleiss kappa etc.) run after recording.

USAGE:
    python3 sp2027/analysis/build_second_audit_packet.py [--seed 20261005]
    python3 sp2027/analysis/record_second_audit.py annotators/second_audit/answers.json
Exit: 0 built; 2 inputs missing.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "sp2027" / "benchmarks"
OUT = ROOT / "sp2027" / "annotators" / "second_audit"

BENCHMARKS = ["Cybench", "NYU CTF Bench", "CVE-Bench",
              "Incalmo", "AgentHarm", "WebSP-Eval"]
DIRS = {"Cybench": "cybench", "NYU CTF Bench": "nyu_ctf_bench",
        "CVE-Bench": "cve_bench", "Incalmo": "incalmo",
        "AgentHarm": "agentharm", "WebSP-Eval": "websp_eval"}

# F1..F9 verbatim from the paper's rubric subsection (sec:framework).
FIELDS = {
    "F1": ("clock boundary",
           "a stated clock boundary: where does measured time start and end?"),
    "F2": ("oracle isolation",
           "an oracle whose grading state and ground truth are isolated from "
           "the agent, verdict access limited to the declared grading "
           "interface (process separation alone is insufficient)"),
    "F3": ("failure retention",
           "retention of failed runs in released artifacts"),
    "F4": ("ordered traces",
           "ordered traces preserved: prompts, tool calls, generated files"),
    "F5": ("hash pinning",
           "hash-pinned generated artifacts and environments"),
    "F6": ("weakness attribution",
           "weakness attribution to a layer: primitive/implementation/"
           "protocol/deployment"),
    "F7": ("discovery/execution separation",
           "separation of discovery from execution work"),
    "F8": ("query accounting",
           "per-request query and cost accounting"),
    "F9": ("reconstruction probe",
           "can an independent party re-derive at least one published "
           "outcome end-to-end from the release alone?"),
}
ALLOWED = ["yes", "partial", "no", "opaque"]


def worksheet_snapshot(bench_dir: Path) -> str:
    """The artifact snapshot block from the first-pass worksheet (sources
    only — the fields table below it is NOT included in any card)."""
    ws = bench_dir / "fields.md"
    if not ws.exists():
        return "(worksheet missing)"
    text = ws.read_text()
    if "```" in text:
        block = text.split("```")[1]
        return "```\n" + block.strip() + "\n```"
    return "(no snapshot block found — record repo URL + commit yourself)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261005)
    args = ap.parse_args()

    summary = BENCH / "summary.csv"
    if not summary.exists() or not all((BENCH / d / "fields.md").exists()
                                       for d in DIRS.values()):
        print("inputs missing: benchmarks/summary.csv or a worksheet")
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cells").mkdir(exist_ok=True)

    cells = []
    for b in BENCHMARKS:
        d = BENCH / DIRS[b]
        snap = worksheet_snapshot(d)
        for f, (name, question) in FIELDS.items():
            cells.append({
                "cell_id": f"{DIRS[b]}::{f}",
                "benchmark": b,
                "field": f,
                "field_name": name,
                "question": question,
                "allowed_values": ALLOWED,
                "evidence_sources": {
                    "worksheet_artifact_snapshot": snap,
                    "evidence_dir": f"sp2027/benchmarks/{DIRS[b]}/evidence/",
                    "worksheet": f"sp2027/benchmarks/{DIRS[b]}/fields.md"
                                 " (inspect sources ONLY; the Field table"
                                 " is withheld until you commit answers)",
                },
            })

    rng = random.Random(args.seed)
    rng.shuffle(cells)

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "seed": args.seed,
        "n_cells": len(cells),
        "note": ("order-blind: the shuffle key is this seed; first-pass "
                 "judgments live in benchmarks/summary.csv and are withheld "
                 "until the auditor commits all 54 answers"),
        "cells_order": [c["cell_id"] for c in cells],
    }
    (OUT / "packet.json").write_text(json.dumps(manifest, indent=2) + "\n")

    for i, c in enumerate(cells, 1):
        if c["field"] == "F9":
            allowed = ("reconstructable", "cannot_reconstruct(reason)",
                       "partial(how far)")
            allowed_txt = ("F9 uses its own outcome vocabulary: start with "
                           "`reconstructable` / `cannot_reconstruct` / "
                           "`partial`, add the reason in parentheses")
        else:
            allowed = ALLOWED
            allowed_txt = (f"{', '.join(ALLOWED)} — yes/partial/no need an "
                           "evidence pointer; opaque needs a one-line search-note")
        (OUT / "cells" / f"{i:02d}_{c['cell_id'].replace('::', '__')}.md").write_text(
            f"# Cell {i:02d}/54 — {c['benchmark']} · {c['field']} ({c['field_name']})\n\n"
            f"**Question (rubric):** {c['question']}\n\n"
            f"**Allowed values:** {allowed_txt}\n\n"
            f"**Sources you may inspect:**\n- {c['evidence_sources']['worksheet_artifact_snapshot']}\n"
            f"- {c['evidence_sources']['evidence_dir']}\n"
            f"- {c['evidence_sources']['worksheet']}\n\n"
            f"**Your judgment:** ______   **Evidence pointer:** ______\n")

    (OUT / "INSTRUCTIONS.md").write_text(
        "# Second-auditor blind packet — 54 cells (6 benchmarks x 9 fields)\n\n"
        f"Order is seeded-shuffled (seed {args.seed}, in packet.json). Work "
        "through the cards in `cells/` in order. For each cell, inspect the "
        "SOURCES ONLY and write your judgment + an evidence pointer on the "
        "card. Do not open benchmarks/summary.csv (or any fields.md Field "
        "table) until every card is committed — the recording script reveals "
        "and scores afterwards, and any peek is a protocol breach to be "
        "logged in the ledger, not hidden.\n\n"
        "Commit: fill the `Your judgment` + `Evidence pointer` blanks, then "
        "run record_answers.py with a JSON of "
        '{"cell_id": {"value": "...", "evidence": "..."}} entries.\n'
        "Disagreements are adjudicated afterwards with notes appended to the "
        "benchmark's evidence file (frozen procedure). Timebox: 2 days.\n")

    (OUT / "record_answers.py").write_text(NEUTRAL_RECORDER)
    print(f"packet built: {OUT}  (54 cells, seed {args.seed})")
    print("next: human second auditor works the cards; then "
          "record_answers.py scores agreement (Fleiss kappa tool ready).")
    return 0


NEUTRAL_RECORDER = '''#!/usr/bin/env python3
"""Neutral second-audit recorder: validates 54 answers, stores them, THEN
reveals first-pass judgments and computes agreement. No peeking before
commit: answers.json must cover all 54 cells or the script exits."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIR_MAP = {"Cybench": "cybench", "NYU CTF Bench": "nyu_ctf_bench",
           "CVE-Bench": "cve_bench", "Incalmo": "incalmo",
           "AgentHarm": "agentharm", "WebSP-Eval": "websp_eval"}
FIELD_COLS = (("F1", "clock"), ("F2", "oracle_independence"),
              ("F3", "failure_retention"), ("F4", "trace"),
              ("F5", "generated_artifacts"), ("F6", "weakness_attribution"),
              ("F7", "discovery_vs_execution"), ("F8", "query_accounting"),
              ("F9", "reconstruction_probe"))

ANSWERS = json.loads(Path(sys.argv[1]).read_text())
packet = json.loads((HERE / "packet.json").read_text())
order = packet["cells_order"]

missing = [c for c in order if c not in ANSWERS]
if missing:
    print(f"INCOMPLETE: {len(missing)} cells missing — commit all 54 first.")
    print("  e.g.", missing[:3]); sys.exit(2)
def norm(v: str) -> str:
    """Normalize both sides of a comparison: strip parenthesized qualifiers
    like cannot_reconstruct(reason) or no(d-n/a), then lowercase."""
    return v.split("(")[0].strip().lower()


def value_ok(cell_id: str, v: str) -> bool:
    if cell_id.endswith("::F9"):
        return norm(v) in ("reconstructable", "cannot_reconstruct", "partial")
    return norm(v) in ("yes", "partial", "no", "opaque")


bad = [c for c, v in ANSWERS.items() if not value_ok(c, v.get("value", ""))]
if bad:
    print("invalid values in:", bad[:5]); sys.exit(2)

(HERE / "answers.committed.json").write_text(
    json.dumps({"committed_utc": datetime.now(timezone.utc).isoformat(),
                "answers": ANSWERS}, indent=2) + "\\n")

summary = (HERE.parents[2] / "sp2027" / "benchmarks" / "summary.csv")
lines = summary.read_text().splitlines()
header = lines[0].split(",")
col_ix = {name: header.index(name) for _, name in FIELD_COLS if name in header}
first_pass = {}
for line in lines[1:]:
    parts = line.split(",")
    if len(parts) < len(header) - 2 or not parts[0].strip():
        continue                      # spare/not-started rows
    bench_dir = DIR_MAP.get(parts[0].strip())
    if bench_dir is None:
        continue
    for f, name in FIELD_COLS:
        if name in col_ix:
            first_pass[f"{bench_dir}::{f}"] = parts[col_ix[name]].split("(")[0].strip()

agree = 0
rows = []
for cell_id in order:
    a = ANSWERS[cell_id]["value"]
    fp = first_pass.get(cell_id, "(unparsed)")
    hit = (norm(a) == norm(fp)) if fp != "(unparsed)" else False
    agree += hit
    rows.append((cell_id, a, fp, hit))
print(f"committed: {len(order)} cells | agreement {agree}/{len(order)} "
      f"({agree/len(order):.1%}) | disagreements {len(order) - agree}")
for cid, a, fp, hit in rows:
    if not hit:
        print(f"  DIFF {cid}: second={a!r} first={fp!r}")
print("next: adjudicate DIFFs with evidence notes appended to the "
      "benchmark evidence file; then fleiss_kappa.py / the statistics lock.")
'''

if __name__ == "__main__":
    sys.exit(main())
