#!/usr/bin/env python3
"""P021/R launcher — full re-run of P021 on APINEX with a free GPT-6 label.

Why this namespace exists: P021 (96 CSPRNG instances, 384 sessions) lost 189
sessions to AgentRouter provider failures, including 86 of the 192 oracle-bearing
sessions. The census (`../CENSUS_P_PROVIDER_20261103.md`) attributed every lost
session to a provider event, so the cohort is re-run end to end rather than
topped up: half of P021's evidence would otherwise sit on a different transport
stack from the other half.

What is identical to P021: frozen runner bytes (hash asserted), the registered
seed list and its receipt, the four cells and their rotation, the prompts, the
two-turn flow, the oracle, the token floor (4200), the session-status
vocabulary, and the analysis predicate.

What differs, and is disclosed: transport (APINEX OpenAI-compatible
/v1/chat/completions instead of AgentRouter Anthropic /v1/messages) and label
(`free/gpt-6-luna` instead of `gpt-6-astra`; APINEX serves no free gpt-6-astra
and the paid route returns HTTP 402). Scheduling is a 10-worker thread pool via
`parallelize_cohort.py`; sessions stay independent, and each row carries
`execution_concurrency` so the parallel run is separable from the serial one.
"""
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

ORIGINAL = ROOT / "info_contract_aesgcm_random_p021_20261102"
OREG = json.loads((ORIGINAL / "_REGISTRATION.json").read_text())
REG = json.loads((HERE / "_REGISTRATION.json").read_text())

FROZEN = ROOT / REG["runner_path"]
got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
if got != REG["runner"]:
    raise SystemExit(f"FROZEN RUNNER HASH MISMATCH: {got} != {REG['runner']}")
if got != OREG["runner"]:
    raise SystemExit("re-run would not use the same runner bytes as P021")

ADAPTER = ROOT / REG["adapter"]
adapter_sha = hashlib.sha256(ADAPTER.read_bytes()).hexdigest()
if adapter_sha != REG["adapter_sha256"]:
    raise SystemExit(f"ADAPTER HASH MISMATCH: {adapter_sha} != {REG['adapter_sha256']}")

spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)
if not hasattr(injected, "ClaudeProvider") or not hasattr(injected, "ProviderFailure"):
    raise SystemExit("injected adapter missing ClaudeProvider/ProviderFailure")
if int(getattr(injected, "P017_TOKEN_FLOOR", 0) or 0) != REG["token_floor"]:
    raise SystemExit("adapter floor does not match the registered floor")

os.environ["APINEX_LABEL_MODEL"] = REG["label"]
import run_info_contract_2x2_aesgcm as base  # noqa: E402

if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did NOT bind the injected provider — aborting")
if base.ClaudeProvider.__module__ != "provider_adapter":
    raise SystemExit(f"unexpected provider module binding: {base.ClaudeProvider.__module__}")

base.OUT = HERE
base.PROTOCOL = REG["protocol"]
base.LABEL = REG["label"]
base.SEEDS = tuple(int(v) for v in REG["seeds"])
_smoke = os.environ.get("ACTS_SEEDS", "").strip()
if _smoke:
    base.SEEDS = tuple(int(v) for v in _smoke.split(",") if v.strip())
base.ROTATIONS = {i: base.ROTATIONS[i % 4] for i in range(max(len(base.SEEDS), 4))}

provider_probe = injected.ClaudeProvider()
launch = {
    "protocol": base.PROTOCOL,
    "namespace": str(HERE.relative_to(ROOT)),
    "rerun_of": str(ORIGINAL.relative_to(ROOT)),
    "rerun_reason": REG["rerun_reason"],
    "model_label": provider_probe.model,
    "route": "apinex",
    "endpoint": provider_probe.endpoint,
    "runner_sha256": got,
    "adapter_sha256": adapter_sha,
    "fixture": REG["fixture"],
    "token_floor": int(injected.P017_TOKEN_FLOOR),
    "token_floor_basis": getattr(injected, "P017_FLOOR_BASIS", None),
    "seeds_registered_sha256": REG.get("seeds_sha256"),
    "seeds": list(base.SEEDS),
    "sessions_registered": 4 * len(base.SEEDS),
    "workers": REG.get("workers"),
    "smoke_seed_override": bool(_smoke),
    "started": time.time(),
}
(HERE / "_LAUNCH.json").write_text(json.dumps(launch, indent=2, sort_keys=True) + "\n")
print(json.dumps(launch, indent=2, sort_keys=True), flush=True)

import parallelize_cohort as pc  # noqa: E402

summary = pc.run(base, HERE, workers=int(REG.get("workers", 10)))
