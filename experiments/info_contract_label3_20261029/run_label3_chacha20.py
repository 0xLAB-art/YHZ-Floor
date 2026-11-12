#!/usr/bin/env python3
"""P010L3-INFO-CONTRACT-2X2-CHACHA20-LABEL3-v1 — wrapper launcher.

Third-label replication of the information-contract 2x2: identical frozen
methodology, DIFFERENT model label (gpt-6-astra on the AgentRouter route).

Two deviations from the P010P wrapper pattern, both disclosed in
PREREGISTRATION.md:

  1. PROVIDER INJECTION: before the frozen runner is imported, the
     AgentRouter transport adapter (provider_adapter_agentrouter.py, whose
     class keeps the frozen name ClaudeProvider for import parity) is loaded
     and registered in sys.modules["provider_adapter"]. The frozen runner's
     own `from provider_adapter import ClaudeProvider, ProviderFailure` then
     binds to the injected module — the frozen file stays byte-for-byte
     untouched (SHA-256 asserted below) and only its transport differs.
  2. TOKEN FLOOR: the frozen runner calls provider.call(prompt, 1400); the
     injected adapter raises the sent budget to 2800 uniformly for all cells
     (reasoning-family label; truncation must not correlate with cell).
     Recorded per-call in request metadata as max_tokens_sent.

Everything else is P010P's pattern: imports the FROZEN P010 runner
byte-for-byte (SHA-256 asserted) and drives it with ONLY namespace / protocol
/ seeds / Latin-square-rotation-mod-4 changes. Prompts, cell slots, fixture,
oracle, policy, feedback strings, temperature provider-default, and turn flow
all come from the frozen module unchanged.

Known cosmetic limitation (same as P010P, disclosed): the frozen module
builds run_id with its own literal prefix; rows are distinguished by the
protocol field and by living in this namespace.

Resume rule (same as P010P, disclosed): interrupted launches resume at SEED
granularity — a seed whose four cells are all terminal is skipped; a partial
seed re-runs its remaining cells AND its completed cells, producing duplicate
(seed, cell) rows; analysis keeps the EARLIEST row per (seed, cell) and flags
later rows as instrument duplicates (recorded, never deleted).
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

FROZEN = ROOT / "run_info_contract_2x2_chacha20.py"
FROZEN_SHA = "a08eab6f4be2401aacf1b39a47ba6960373164dcc57640d3672d8c36583ee198"
got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
if got != FROZEN_SHA:
    raise SystemExit(f"FROZEN RUNNER HASH MISMATCH: {got}")

# --- provider injection (deviation 1) -------------------------------------
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
if base.ClaudeProvider.__module__ != "provider_adapter":
    raise SystemExit(f"unexpected provider module binding: {base.ClaudeProvider.__module__}")

base.OUT = HERE
base.PROTOCOL = "P010L3-INFO-CONTRACT-2X2-CHACHA20-LABEL3-v1"
# The frozen module creates its artifact subdirectories at import time under
# ITS OWN OUT; re-create them under the patched namespace before main().
for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (HERE / sub).mkdir(parents=True, exist_ok=True)
SEEDS = tuple(int(v) for v in os.environ.get(
    "ACTS_SEEDS", "201,202,203,204,205,206,207,208").split(",") if v.strip())
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
