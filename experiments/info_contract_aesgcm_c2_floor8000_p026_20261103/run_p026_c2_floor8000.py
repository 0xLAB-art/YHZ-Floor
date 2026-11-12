#!/usr/bin/env python3
"""P026 — C2 floor-sensitivity cohort (single-cell, floor 8000).

Root cause established in EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md: C2
(withheld premise, oracle-bearing) sessions exhaust the registered 4200-token
floor during hidden reasoning in ~53% of sessions; the route then surfaces an
empty text block (HTTP 200, output_tokens == floor exactly, stop_reason
"length"), which the adapter records as EMPTY_RESPONSE. Those sessions are
unscored, so C2's evaluable n drops from 96 to ~45 per cohort.

This cohort re-runs the SAME 96 seeds, SAME label, SAME fixture, prompts,
oracle and predicate — C2 only — with the adapter floor raised to 8000, so
deliberation that outlasted 4200 can finish and be scored.

Registered prediction (falsifiable):
  1. EMPTY_RESPONSE rate at floor 8000 falls to ~0 (any remainder = the tail
     of the deliberation distribution beyond 8000).
  2. Acceptance stays 0/96 — the withheld premise strands the agent regardless
     of budget; recovered sessions become ORACLE_FAIL with full text.
  3. The recovered output-token distribution completes the causal analysis:
     empties were the >4200 half of C2's deliberation distribution.

The registered 4200-floor cohorts are NOT modified; this is a separately
registered sensitivity cohort, disclosed here before its first call.
"""
import hashlib, importlib.util, json, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

ADAPTER = ROOT / "provider_adapter_agentrouter_p026_floor8000.py"
ADAPTER_SHA = hashlib.sha256(ADAPTER.read_bytes()).hexdigest()
SOURCE_NS = "info_contract_aesgcm_random_p021ar_20261103"
SOURCE_REG = json.loads((ROOT / SOURCE_NS / "_REGISTRATION.json").read_text())
SEEDS = tuple(int(s) for s in SOURCE_REG["seeds"])
LABEL = SOURCE_REG["label"]
PROTOCOL = "P026-INFO-CONTRACT-C2-FLOOR8000-AESGCM-CSPRNG-SEEDS-v1"

reg = {
    "protocol": PROTOCOL,
    "registered": "2026-11-03",
    "registered_before_first_call": True,
    "purpose": ("floor-sensitivity: recover C2 sessions lost to the 4200-token "
                "floor-exhaustion mechanism documented in "
                "EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md"),
    "source_namespace": SOURCE_NS,
    "rerun_of": SOURCE_NS,
    "seeds": list(SEEDS),
    "seeds_source": f"{SOURCE_NS}/_REGISTRATION.json (identical seeds, byte-identical)",
    "cells": ["C2"],
    "label": LABEL,
    "fixture": "aesgcm",
    "token_floor_registered_cohorts": 4200,
    "token_floor_this_cohort": 8000,
    "adapter": ADAPTER.name,
    "adapter_sha256": ADAPTER_SHA,
    "adapter_delta": "P017_TOKEN_FLOOR 4200 -> 8000; every other byte identical to provider_adapter_agentrouter_p023.py",
    "workers": 6,
    "predictions": [
        "EMPTY_RESPONSE rate at floor 8000 falls to ~0",
        "acceptance stays 0/96 (withheld premise strands the agent at any budget)",
        "recovered sessions become ORACLE_FAIL with full text",
    ],
}
(HERE / "_REGISTRATION.json").write_text(json.dumps(reg, indent=1, sort_keys=True) + "\n")

os.environ["AGENTROUTER_LABEL_MODEL"] = LABEL
os.environ.setdefault("ACTS_FAILURE_LOG", str(HERE / "failure_log.jsonl"))

spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)

import run_info_contract_2x2_aesgcm as base  # noqa: E402
if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did not bind the injected provider")

base.OUT = HERE
base.PROTOCOL = PROTOCOL
base.SEEDS = SEEDS
base.CELLS = ("C2",)
base.ROTATIONS = {pos: ("C2",) for pos in range(len(SEEDS))}

manifest = {
    "protocol": PROTOCOL,
    "seeds": len(SEEDS), "cells": ["C2"], "sessions_planned": len(SEEDS),
    "token_floor": 8000,
    "basis": "EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md",
    "registered": reg["registered"],
}
(HERE / "_P026_MANIFEST.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
print(json.dumps(manifest, indent=1), flush=True)

import parallelize_cohort as pc  # noqa: E402
summary = pc.run(base, base.OUT, workers=6, phase="p026_floor8000")
print(json.dumps(summary.get("per_cell", {}), indent=1), flush=True)
