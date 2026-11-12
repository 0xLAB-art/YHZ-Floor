#!/usr/bin/env python3
"""P021/AR launcher — full re-run of P021 on AgentRouter with the original label.

Why AgentRouter and not APINEX: P021 was run on `gpt-6-astra`, and APINEX neither
serves it on the free plan nor on a zero balance (HTTP 402). The free labels there
solve the bearing cell at 0–25% against P021's 55%, so an APINEX re-run would
measure a substitute model, not P021's design. AgentRouter still serves the
original label.

Why the transport should behave better than P021 did: P021 used the P017 adapter,
which sent no retry policy and inherited a router-side 400 defect
(`stream_options` set without `stream`) plus unretried 5xx/empty responses. This
launcher binds the P023 adapter, which never sends either stream parameter,
retries the registered transient classes with backoff, and was used by P024A with
0 provider failures in 96 sessions.

Identical to P021: frozen runner bytes (hash asserted against both
registrations), the 96 registered CSPRNG seeds, cells and rotation, prompts,
two-turn flow, oracle, status vocabulary, and the 4200-token floor.

Disclosed differences: adapter (P023 retry transport instead of P017), 8-worker
thread pool via `parallelize_cohort.py`, and a failure log so every retried
attempt is auditable.
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

os.environ["AGENTROUTER_LABEL_MODEL"] = REG["label"]
os.environ.setdefault("ACTS_FAILURE_LOG", str(HERE / "failure_log.jsonl"))
import run_info_contract_2x2_aesgcm as base  # noqa: E402

if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did NOT bind the injected provider — aborting")

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
    "route": "agentrouter",
    "endpoint": getattr(provider_probe, "endpoint", None),
    "runner_sha256": got,
    "adapter": REG["adapter"],
    "adapter_sha256": adapter_sha,
    "retry_policy": getattr(injected, "P023_POLICY", None),
    "token_floor": int(injected.P017_TOKEN_FLOOR),
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

summary = pc.run(base, HERE, workers=int(REG.get("workers", 8)))
