#!/usr/bin/env python3
"""P010L4-INFO-CONTRACT-2X2-CHACHA20-LABEL4-v1 — wrapper launcher.

Fourth-label replication of the information-contract 2x2: identical frozen
methodology, DIFFERENT model label (gpt-5.6-sol on the AgentRouter route).

Designation note (disclosed in PREREGISTRATION.md): the project owner
designated the opus label (claude-opus-5-5) for this cohort; the gateway
returned HTTP 503 for every opus identifier variant across both keys (12/12
attempts, recorded in HEALTH.json) while the gpt labels responded normally,
so the label was selected from the gateway's own attested list: gpt-5.6-sol,
a version of the GPT family not used by any prior cohort.

Deviations from the P010P wrapper pattern, disclosed:

  1. PROVIDER INJECTION (same as P010L2/L3): the AgentRouter transport adapter
     is registered as sys.modules["provider_adapter"] before the frozen runner
     is imported; the frozen file stays byte-for-byte untouched (SHA-256
     asserted) and only its transport differs.
  2. TOKEN FLOOR (same as P010L2/L3): 1400 -> 2800 uniformly for all cells
     (reasoning-family label; truncation must not correlate with cell).
     Recorded per-call as max_tokens_sent.
  3. LABEL BINDING (the X1 lesson, new): the label is bound twice -- via
     AGENTROUTER_LABEL_MODEL before import AND asserted post-run by a raw-
     response fingerprint audit (every raw response's model field must echo
     gpt-5.6-sol; any mismatch voids the cohort's label claims).

Everything else is P010P's pattern: imports the FROZEN P010 runner
byte-for-byte (SHA-256 asserted) and drives it with ONLY namespace / protocol
/ seeds / Latin-square-rotation changes.

Resume rule (same as P010P/L3, disclosed): interrupted launches resume at SEED
granularity; duplicate (seed, cell) rows resolved by the earliest-row rule.
Provider-failure sessions are terminal and never retried.
"""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[0]  # sp2027/research_execution
sys.path.insert(0, str(ROOT))

LABEL = "gpt-5.6-sol"
os.environ["AGENTROUTER_LABEL_MODEL"] = LABEL

FROZEN = ROOT / "run_info_contract_2x2_chacha20.py"
FROZEN_SHA = "a08eab6f4be2401aacf1b39a47ba6960373164dcc57640d3672d8c36583ee198"
got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
if got != FROZEN_SHA:
    raise SystemExit(f"FROZEN RUNNER HASH MISMATCH: {got}")

ADAPTER = ROOT / "provider_adapter_agentrouter.py"
ADAPTER_SHA = "d26dd920d8c2dda1d4ef919daa07d3e82dcd8109f14175e335f2da428aaaa3dc"
adapter_sha = hashlib.sha256(ADAPTER.read_bytes()).hexdigest()
if adapter_sha != ADAPTER_SHA:
    raise SystemExit(f"ADAPTER HASH MISMATCH: {adapter_sha}")
spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)
if not hasattr(injected, "ClaudeProvider") or not hasattr(injected, "ProviderFailure"):
    raise SystemExit("injected adapter missing ClaudeProvider/ProviderFailure")

import run_info_contract_2x2_chacha20 as base  # noqa: E402

if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did NOT bind the injected provider — aborting")

base.OUT = HERE
base.PROTOCOL = "P010L4-INFO-CONTRACT-2X2-CHACHA20-LABEL4-v1"
for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (HERE / sub).mkdir(parents=True, exist_ok=True)
SEEDS = tuple(int(v) for v in os.environ.get(
    "ACTS_SEEDS", "211,212,213,214,215,216,217,218").split(",") if v.strip())
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
