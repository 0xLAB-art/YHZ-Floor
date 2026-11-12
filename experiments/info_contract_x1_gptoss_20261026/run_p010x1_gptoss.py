#!/usr/bin/env python3
"""P010X1-INFO-CONTRACT-2X2-CHACHA20-GPTOSS120B-v1 — wrapper launcher.

Imports the FROZEN P010 runner module byte-for-byte (SHA-256 asserted
below) and drives it with the cross-vendor configuration. ZERO methodology
code lives in this file: prompts, cell slots, fixture, oracle, policy,
feedback strings, turn flow, and the provider adapter all come from the
frozen module's own constants and functions. What the wrapper sets:

  OUT       -> this namespace (all artifacts land here)
  PROTOCOL  -> P010X1-INFO-CONTRACT-2X2-CHACHA20-GPTOSS120B-v1
  SEEDS     -> fresh seeds 161-176 (ACTS_SEEDS overridable)
  ROTATIONS -> the frozen 4-seed Latin square applied modulo 4
  env       -> ACTS_PROVIDER_ENDPOINT=http://127.0.0.1:11434/v1,
               ACTS_PROVIDER_MODEL=gpt-oss:120b-cloud, and the Anthropic
               key env cleared. These are the variables the frozen module's
               own provider_adapter.ClaudeProvider already reads; the
               provider redirect is pure configuration, not code.

Provider-attestation disclosure: the model tag is provider-attested via
the Ollama cloud route (free tier), NOT digest-pinned. See
PREREGISTRATION.md.

Resume rule (disclosed): same seed-granularity rule as the n16 wrapper;
duplicate (seed, cell) rows resolved by keeping the earliest row and
flagging later ones as instrument duplicates. Provider-failure sessions
(including free-plan cap errors) are terminal and never retried.
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

# Provider redirect via configuration only (variables the frozen adapter reads).
os.environ["ACTS_PROVIDER_ENDPOINT"] = "http://127.0.0.1:11434/v1"
os.environ["ACTS_PROVIDER_MODEL"] = "gpt-oss:120b-cloud"
os.environ.pop("ACTS_PROVIDER_API_KEY", None)

import run_info_contract_2x2_chacha20 as base  # noqa: E402

base.OUT = HERE
base.PROTOCOL = "P010X1-INFO-CONTRACT-2X2-CHACHA20-GPTOSS120B-v1"
for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (HERE / sub).mkdir(parents=True, exist_ok=True)
SEEDS = tuple(int(v) for v in os.environ.get(
    "ACTS_SEEDS", "161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176").split(",") if v.strip())
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
