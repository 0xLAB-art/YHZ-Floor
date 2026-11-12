#!/usr/bin/env python3
"""Amendment A3 top-up: re-run only the pairs whose first pass returned an empty
response from the router.

Scope is deliberately narrow:
* only (seed, cell) pairs whose first-pass row has status EMPTY_RESPONSE;
* only those pairs — `base.CELLS` and the per-seed rotation are both filtered, so
  no completed session is repeated;
* output goes to `amendment_a3/`, never appended to the first-pass
  `results.jsonl`;
* every row carries `amendment: "A3"` and the driver records the source pair list.

The first pass stays the primary record. Any analysis that uses this pass must
report the primary and amended counts side by side.
"""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

REG = json.loads((HERE / "_REGISTRATION.json").read_text())
ADAPTER = ROOT / REG["adapter"]
if hashlib.sha256(ADAPTER.read_bytes()).hexdigest() != REG["adapter_sha256"]:
    raise SystemExit("adapter hash mismatch")
os.environ["AGENTROUTER_LABEL_MODEL"] = REG["label"]
os.environ.setdefault("ACTS_FAILURE_LOG", str(HERE / "amendment_a3" / "failure_log.jsonl"))

spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)

import run_info_contract_2x2_aesgcm as base  # noqa: E402
if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did not bind the injected provider")

rows = [json.loads(line) for line in (HERE / "results.jsonl").read_text().splitlines() if line.strip()]
failed = {(int(r["seed"]), r["cell"]) for r in rows if r["status"] == "EMPTY_RESPONSE"}
if not failed:
    raise SystemExit("no EMPTY_RESPONSE pairs to top up")

seeds = tuple(int(s) for s in REG["seeds"])
orig_rot = {i: base.ROTATIONS[i % 4] for i in range(len(seeds))}
affected = [i for i, s in enumerate(seeds) if any((s, c) in failed for c in ("C1", "C2", "C3", "C4"))]

base.OUT = HERE / "amendment_a3"
base.OUT.mkdir(exist_ok=True)
base.PROTOCOL = REG["protocol"] + "-A3-TOPUP"
base.SEEDS = tuple(seeds[i] for i in affected)
base.CELLS = tuple(sorted({c for (_, c) in failed}))
base.ROTATIONS = {pos: tuple(c for c in orig_rot[i] if (seeds[i], c) in failed)
                  for pos, i in enumerate(affected)}

manifest = {
    "amendment": "A3",
    "source_namespace": HERE.name,
    "source_protocol": REG["protocol"],
    "basis": "pairs whose first pass returned EMPTY_RESPONSE from the router",
    "affected_seeds": len(affected),
    "pairs": sorted([s, c] for s, c in failed),
    "cells": list(base.CELLS),
    "sessions_planned": sum(len(v) for v in base.ROTATIONS.values()),
    "note": "first-pass rows are untouched; this pass is reported separately",
}
(base.OUT / "_A3_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
print(json.dumps(manifest, indent=2, sort_keys=True), flush=True)

import parallelize_cohort as pc  # noqa: E402
summary = pc.run(base, base.OUT, workers=6, phase="amendment_a3")
