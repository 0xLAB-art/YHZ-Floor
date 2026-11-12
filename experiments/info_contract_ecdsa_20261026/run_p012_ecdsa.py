#!/usr/bin/env python3
"""P012-INFO-CONTRACT-2X2-ECDSA-NONCE-REUSE-v1 — wrapper launcher.

Imports the P012 runner module byte-for-byte (SHA-256 asserted below) and
drives it with the n=16 configuration. ZERO methodology code lives in this
file: prompts, cell slots, fixture, oracle, policy, feedback strings, turn
flow, and the provider adapter all come from the P012 module's own constants
and functions (itself copied from the frozen P010 module). What the wrapper
sets:

  OUT       -> this namespace (all artifacts land here)
  SEEDS     -> fresh seeds 141-156 (ACTS_SEEDS overridable)
  ROTATIONS -> the frozen 4-seed Latin square applied modulo 4 (16 seeds =
               four balanced squares)

Known cosmetic limitation (disclosed in PREREGISTRATION.md): run_ids carry
the P012 module's own prefix; rows are distinguished by their protocol
field and by living in this namespace.

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

FROZEN = ROOT / "run_info_contract_2x2_ecdsa.py"
FROZEN_SHA = "8e67d904a08409d1489219bb4043a86259810340b87a86e449c3be2660ff60f0"
got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
if got != FROZEN_SHA:
    raise SystemExit(f"FROZEN RUNNER HASH MISMATCH: {got}")

import run_info_contract_2x2_ecdsa as base  # noqa: E402

base.OUT = HERE
base.PROTOCOL = "P012-INFO-CONTRACT-2X2-ECDSA-NONCE-REUSE-v1"
for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (HERE / sub).mkdir(parents=True, exist_ok=True)
SEEDS = tuple(int(v) for v in os.environ.get(
    "ACTS_SEEDS", "141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156").split(",") if v.strip())
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
