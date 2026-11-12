#!/usr/bin/env python3
"""Historical W3 fill-night driver (superseded and fail-closed).

The terminal E2/W3 state failed to complete at 33/270. The campaign guard
refuses the mutation path below; the implementation remains as provenance for
the pre-campaign fill design.

Gate: >= 250 graded sessions in runs_e2 (same G1 rule as w6_transform.py).
Refuses below it — the paper stays frozen until the corpus is real.

Sequence (runbook order; nothing enters the paper un-re-derived):
  step 0  acts_audit validate            (exit 0 required, HARD gate)
  step 1  w3_fill.py --emit-tex          (Table 3 + prose evidence)
  step 2  bounds_tier.py                 (KM + three-way outage band)
  step 3  aor_decompose.py               (latency decomposition + Fig-3 pairs)
  step 4  e4_sensitivity.py --campaign   (the single [PENDING-W4] mark)

Outputs land in sp2027/analysis/fill_night_<UTCdate>/ plus copies of the
evidence JSONs at their canonical paths (w3_fill_evidence.json etc. stay
where the lock expects them). Steps 5-6 (lock x2, paper edits, PDF) remain
deliberately human-per-runbook; this tool prints the exact post-steps.

Usage: python3 sp2027/analysis/fill_night.py [--dry-run]
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R2C = ROOT / "sp2027" / "agent-eval" / "runs_e2"
AN = ROOT / "sp2027" / "analysis"
sys.path.insert(0, str(ROOT / "sp2027" / "ops"))
from campaign_guard import require_continuation_authorized  # noqa: E402


def graded_count() -> int:
    idx = R2C / "INDEX.jsonl"
    n = 0
    non_attack = {"PROVIDER_UNAVAILABLE", "HARNESS_ERROR"}
    if idx.exists():
        for line in idx.read_text().splitlines():
            if not line.strip():
                continue
            try:
                st = json.loads(line).get("status")
            except Exception:                                # noqa: BLE001
                continue
            if st not in non_attack:
                n += 1
    return n


def run(step: str, cmd: list[str], outdir: Path) -> bool:
    print(f"\n=== step {step}: {' '.join(cmd)}", flush=True)
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    (outdir / f"step{step}.log").write_text(
        f"$ {' '.join(cmd)}\n\n--- stdout ---\n{p.stdout}\n--- stderr ---\n{p.stderr}\n"
        f"--- exit: {p.returncode} ---\n")
    tail = (p.stdout or p.stderr).strip().splitlines()[-3:]
    for t in tail:
        print(f"  | {t}", flush=True)
    print(f"  exit={p.returncode}", flush=True)
    return p.returncode == 0


def main() -> int:
    dry = "--dry-run" in sys.argv
    if not dry:
        try:
            require_continuation_authorized("fill-night analysis chain")
        except RuntimeError as exc:
            print(exc, flush=True)
            return 2
    g = graded_count()
    print(f"G1 graded sessions: {g} (need >= 250)", flush=True)
    if g < 250:
        print("G1 FAIL: fill night is not armed. The paper stays frozen.",
              flush=True)
        return 1
    stamp = time.strftime("%Y-%m-%d", time.gmtime())
    outdir = AN / f"fill_night_{stamp}"
    if dry:
        print(f"[dry-run] would create {outdir} and execute steps 0-4",
              flush=True)
        return 0
    outdir.mkdir(exist_ok=True)
    ok = True
    # step 0 — HARD gate
    ok0 = run("0", ["python3", "sp2027/schema/acts_audit.py", "validate",
                    "sp2027/agent-eval/runs_e2", "--format", "text"], outdir)
    if not ok0:
        print("STEP 0 HARD FAIL: a corpus row failed the validator. "
              "Stop; no fill runs.", flush=True)
        return 2
    # step 1 — primary numbers
    ok1 = run("1", ["python3", "sp2027/analysis/w3_fill.py", "--emit-tex"],
              outdir)
    # step 2 — KM / bounds tiers
    ok2 = run("2", ["python3", "sp2027/analysis/bounds_tier.py",
                    "--claim", "median time-to-success < 900 s"], outdir)
    # step 3 — AOR decomposition
    ok3 = run("3", ["python3", "sp2027/analysis/aor_decompose.py",
                    "sp2027/agent-eval/runs_e2"], outdir)
    # step 4 — E4 sensitivity (the [PENDING-W4] mark)
    ok4 = run("4", ["python3", "sp2027/analysis/e4_sensitivity.py",
                    "--campaign", "sp2027/agent-eval/runs_e2",
                    "--skip-missing"], outdir)
    # snapshot canonical evidence files into the night's dir
    for f in ("w3_fill_evidence.json", "w3_fill_table3.tex",
              "bounds_tier_evidence.json", "aor_runs_e2.json",
              "e4_sensitivity_results.json"):
        src = AN / f
        if src.exists():
            shutil.copy2(src, outdir / f)
    steps_ok = {"0": ok0, "1": ok1, "2": ok2, "3": ok3, "4": ok4}
    (outdir / "SUMMARY.json").write_text(json.dumps(
        {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "graded": g, "steps": steps_ok}, indent=1))
    print("\n=== fill-night summary ===", flush=True)
    for k, v in steps_ok.items():
        print(f"  step {k}: {'OK' if v else 'FAIL'}", flush=True)
    print(f"  evidence dir: {outdir}", flush=True)
    if not all(steps_ok.values()):
        print("One or more steps FAILED — read the step logs before "
              "anything touches the paper.", flush=True)
        return 3
    print("\nPOST-STEPS (human, per runbook steps 5-6):\n"
          "  1. python3 sp2027/analysis/results_lock.py   # x2, expect convergence\n"
          "  2. Edit paper/main.tex: replace [PENDING-W3]/[PENDING-W4] marks\n"
          "     from the emitted evidence; update PAPER_HEADER_CENSUS;\n"
          "     add the re-derivation claims to CLAIMS.\n"
          "  3. pdflatex x3 + bibtex; body <= 13pp.\n"
          "  4. Ledger row + commit.\n", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
