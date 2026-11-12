#!/usr/bin/env python3
"""P010N16-INFO-CONTRACT-2X2-CHACHA20-N16-v1 — wrapper launcher.

Imports the FROZEN P010 runner module byte-for-byte (SHA-256 asserted below)
and drives it with the n=16 configuration. ZERO methodology code lives in
this file: prompts, cell slots, fixture, oracle, policy, feedback strings,
turn flow, and the provider adapter all come from the frozen module's own
constants and functions. What the wrapper sets:

  OUT       -> this namespace (all artifacts land here)
  PROTOCOL  -> P010N16-INFO-CONTRACT-2X2-CHACHA20-N16-v1
  SEEDS     -> fresh seeds 121-136 (ACTS_SEEDS overridable)
  ROTATIONS -> the frozen 4-seed Latin square applied modulo 4 (16 seeds =
               four balanced squares)

Known cosmetic limitation (disclosed in PREREGISTRATION.md): the frozen
module builds run_id with its own literal prefix, so session run_ids carry
the original cohort's prefix; rows are distinguished by their protocol field
and by living in this namespace.

Resume rule (disclosed): interrupted launches resume at SEED granularity.
A seed whose four cells are all terminal is skipped; a partially recorded
seed re-runs its remaining cells AND its completed cells, producing
duplicate (seed, cell) rows; analysis keeps the EARLIEST row per (seed,
cell) and flags later rows as instrument duplicates (recorded, never
deleted). Provider-failure sessions are terminal and never retried.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[0]
sys.path.insert(0, str(ROOT))

FROZEN = ROOT / "run_info_contract_2x2_chacha20.py"
FROZEN_SHA = "a08eab6f4be2401aacf1b39a47ba6960373164dcc57640d3672d8c36583ee198"
got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
if got != FROZEN_SHA:
    raise SystemExit(f"FROZEN RUNNER HASH MISMATCH: {got}")

import run_info_contract_2x2_chacha20 as base  # noqa: E402

base.OUT = HERE
base.PROTOCOL = "P010N16-INFO-CONTRACT-2X2-CHACHA20-N16-v1"
# The frozen module creates its artifact subdirectories at import time under
# ITS OWN OUT; re-create them under the patched namespace before main().
for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (HERE / sub).mkdir(parents=True, exist_ok=True)
SEEDS = tuple(int(v) for v in os.environ.get(
    "ACTS_SEEDS", "121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136").split(",") if v.strip())
base.SEEDS = SEEDS
base.ROTATIONS = {i: base.ROTATIONS[i % 4] for i in range(max(len(SEEDS), 4))}

if (HERE / "results.jsonl").exists():
    recorded = {}
    for line in (HERE / "results.jsonl").read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            recorded.setdefault(rec["seed"], set()).add(rec["cell"])
    complete = {s for s, cells in recorded.items() if cells >= set(base.CELLS)}
    if complete:
        base.SEEDS = tuple(s for s in base.SEEDS if s not in complete)
        (HERE / "resume_note.json").write_text(json.dumps(
            {"skipped_complete_seeds": sorted(complete),
             "seeds_to_run": list(base.SEEDS)}, indent=1, sort_keys=True) + "\n")

base.main()
