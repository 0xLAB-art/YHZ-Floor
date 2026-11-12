#!/usr/bin/env python3
"""P024 arm launcher (AES-GCM, 24 shared CSPRNG instances, paired labels).

Injects the P024 adapter into the frozen runner, asserts runner/adapter hashes
against _REGISTRATION.json, sets the registered token floor before the adapter
is imported, and writes _LAUNCH.json before the first provider call.

One file serves both arms: protocol, label, seeds and floor come from the
arm's own _REGISTRATION.json.
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

REG = json.loads((HERE / "_REGISTRATION.json").read_text())
FROZEN = ROOT / REG["runner_path"]
got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
if got != REG["runner"]:
    raise SystemExit(f"FROZEN RUNNER HASH MISMATCH: {got} != {REG['runner']}")

ADAPTER = ROOT / REG["adapter"]
adapter_sha = hashlib.sha256(ADAPTER.read_bytes()).hexdigest()
if adapter_sha != REG["adapter_sha256"]:
    raise SystemExit(f"ADAPTER HASH MISMATCH: {adapter_sha} != {REG['adapter_sha256']}")

os.environ["ACTS_TOKEN_FLOOR"] = str(REG["token_floor"])
spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)
if not hasattr(injected, "ClaudeProvider") or not hasattr(injected, "ProviderFailure"):
    raise SystemExit("injected adapter missing ClaudeProvider/ProviderFailure")
if int(getattr(injected, "P017_TOKEN_FLOOR", 0)) != REG["token_floor"]:
    raise SystemExit("adapter floor does not match the registered floor")

os.environ["AGENTROUTER_LABEL_MODEL"] = REG["label"]
os.environ["ACTS_FAILURE_LOG"] = str(HERE / "failure_log.jsonl")
import run_info_contract_2x2_aesgcm as base  # noqa: E402

if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did NOT bind the injected provider — aborting")
if base.ClaudeProvider.__module__ != "provider_adapter":
    raise SystemExit(f"unexpected provider module binding: {base.ClaudeProvider.__module__}")

for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (HERE / sub).mkdir(parents=True, exist_ok=True)

base.OUT = HERE
base.PROTOCOL = REG["protocol"]
base.LABEL = REG["label"]
base.SEEDS = tuple(int(v) for v in REG["seeds"])
base.ROTATIONS = {i: base.ROTATIONS[i % 4] for i in range(max(len(base.SEEDS), 4))}

provider_probe = injected.ClaudeProvider()  # resolves endpoint/model/key; no call
launch = {
    "protocol": base.PROTOCOL,
    "namespace": str(HERE.relative_to(ROOT)),
    "supersedes_design_of": REG.get("same_design_as"),
    "model_label": provider_probe.model,
    "route": "agentrouter",
    "endpoint_host": provider_probe.endpoint.split("//")[-1].split("/")[0],
    "runner_sha256": got,
    "adapter_sha256": adapter_sha,
    "transport_policy": getattr(injected, "P023_POLICY", None),
    "fixture": "aesgcm",
    "fixture_name": "AES-GCM",
    "keystream_exposed": True,
    "seed_receipt": REG.get("seed_receipt"),
    "seeds_registered_sha256": REG.get("seeds_sha256"),
    "token_floor": int(REG["token_floor"]),
    "token_floor_probe": REG.get("token_floor_probe"),
    "paired_arm": REG.get("paired_arm"),
    "seeds": list(base.SEEDS),
    "sessions_registered": 4 * len(base.SEEDS),
    "user_agent": getattr(injected, "P017_UA", None),
    "started": time.time(),
}
(HERE / "_LAUNCH.json").write_text(json.dumps(launch, indent=2, sort_keys=True) + "\n")
print(json.dumps(launch, indent=2, sort_keys=True), flush=True)

# Scheduling (declared in AMENDMENT_scheduling_20261103.md). Sessions are
# independent, so they run on a pool; resumption is at (seed, cell) granularity
# so the registered rotation index is never re-derived from a shortened list.
PARALLEL = int(os.environ.get("ACTS_CONCURRENCY", "10") or 1)

if PARALLEL <= 1 and (HERE / "results.jsonl").exists():
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

if PARALLEL > 1:
    from parallelize_cohort import run as run_parallel
    run_parallel(base, HERE, PARALLEL)
else:
    base.main()
