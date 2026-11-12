#!/usr/bin/env python3
"""P022b launcher (AES-GCM, CSPRNG-drawn instances, 4200-token floor, gpt-5.6-sol).

Same injection pattern as P014-P021: the P017 adapter is registered in
sys.modules["provider_adapter"] before the frozen runner import, the runner
bytes are asserted against _REGISTRATION.json, and _LAUNCH.json is written
before the first provider call.

P022 repairs the P016 generality gap: the same 24 CSPRNG instances run on two
label arms (b: gpt-5.6-sol here, a: gpt-6.1-sol in the sibling directory) for
a paired cross-label comparison. Launched only after P021 and P022a have
fully exited, so one key never carries two cohorts at once.
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

spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)
if not hasattr(injected, "ClaudeProvider") or not hasattr(injected, "ProviderFailure"):
    raise SystemExit("injected adapter missing ClaudeProvider/ProviderFailure")
if int(getattr(injected, "P017_TOKEN_FLOOR", 0)) != REG["token_floor"]:
    raise SystemExit("adapter floor does not match the registered floor")

os.environ["AGENTROUTER_LABEL_MODEL"] = REG["label"]
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
    "namespace": "info_contract_aesgcm_p022b_20261102",
    "model_label": provider_probe.model,
    "route": "agentrouter",
    "endpoint_host": provider_probe.endpoint.split("//")[-1].split("/")[0],
    "runner_sha256": got,
    "adapter_sha256": adapter_sha,
    "fixture": "aesgcm",
    "fixture_name": "AES-GCM",
    "keystream_exposed": True,
    "seed_receipt": REG.get("seed_receipt"),
    "seeds_registered_sha256": REG.get("seeds_sha256"),
    "paired_arm": REG.get("paired_arm"),
    "token_floor": int(injected.P017_TOKEN_FLOOR),
    "token_floor_basis": getattr(injected, "P017_FLOOR_BASIS", None),
    "seeds": list(base.SEEDS),
    "sessions_registered": 4 * len(base.SEEDS),
    "user_agent": getattr(injected, "P017_UA", None),
    "started": time.time(),
}
(HERE / "_LAUNCH.json").write_text(json.dumps(launch, indent=2, sort_keys=True) + "\n")
print(json.dumps(launch, indent=2, sort_keys=True), flush=True)

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
