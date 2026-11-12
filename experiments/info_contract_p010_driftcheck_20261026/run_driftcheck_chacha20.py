"""P010 drift-check rerun: same protocol, same label, ORIGINAL seeds 41--44.

Launched 2026-10-26, after the powered cohort (seeds 101--108) and the
second-label replication (seeds 111--118) were known.  Purpose: separate
temporal drift (same seeds re-run later -> different outcomes) from seed
heterogeneity (same seeds reproduce; the powered cohort's C2 0/8 then
reflects seed composition, not a changed environment).  This is a
reproducibility rerun under the original pre-specification (base runner
byte-identical, model label claude-sonnet-4-6-free), NOT a new
confirmatory cohort; it is not pooled with any existing cohort.

Resume: sessions already present in results.jsonl are skipped.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent  # research_execution/
sys.path.insert(0, str(SRC))

import run_info_contract_2x2_chacha20 as base  # noqa: E402

# Patch the namespace BEFORE main(): artifacts land here, not in the
# original cohort directory.  Protocol string and label are kept identical
# on purpose (same-label requirement).
base.OUT = HERE
for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (HERE / sub).mkdir(exist_ok=True)

SEEDS = tuple(
    int(v) for v in
    __import__("os").environ.get("ACTS_SEEDS", "41,42,43,44").split(",")
    if v.strip()
)
base.SEEDS = SEEDS

# Resume support (same pattern as the powered cohort runner).
complete = set()
results_path = HERE / "results.jsonl"
if results_path.is_file():
    for line in results_path.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            complete.add((row["seed"], row["cell"]))
if complete:
    base.SEEDS = tuple(s for s in base.SEEDS
                       if any((s, c) not in complete for c in base.CELLS))
    (HERE / "resume_note.json").write_text(json.dumps(
        {"completed_sessions": sorted([list(x) for x in complete]),
         "seeds_remaining": list(base.SEEDS)}, indent=1, sort_keys=True) + "\n")

base.main()

# Post-run provenance stamp (run_info.json is written by base.main() with
# the original cohort's field set; annotate it as a drift-check rerun).
ri_path = HERE / "run_info.json"
ri = json.loads(ri_path.read_text())
ri["rerun_of"] = "info_contract_2x2_20261018 (original P010 cohort)"
ri["rerun_kind"] = "drift-check (reproducibility; same protocol, same label, original seeds)"
ri["rerun_launched_utc"] = "2026-10-26"
ri["pooled_with_other_cohorts"] = False
ri_path.write_text(json.dumps(ri, indent=2, sort_keys=True) + "\n")
print("run_info annotated as drift-check rerun")
