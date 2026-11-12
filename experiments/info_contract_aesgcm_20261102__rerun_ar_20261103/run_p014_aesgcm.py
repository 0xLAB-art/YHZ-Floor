#!/usr/bin/env python3
"""P014 AES-GCM cohort launcher (wrapper).

Injects the AgentRouter transport adapter before importing the frozen P014
runner, asserts the runner bytes against `_REGISTRATION.json`, sets the cohort
namespace and seeds, and writes `_LAUNCH.json` (adapter SHA, model label,
endpoint host) BEFORE the first provider call.

Deviation surface is identical to the one disclosed for P010L3/P011:

  1. PROVIDER INJECTION: transport adapter registered in
     sys.modules["provider_adapter"] before the runner import; the runner file
     stays byte-for-byte untouched and its SHA is asserted.
  2. TOKEN FLOOR: the injected adapter raises the sent budget to 2800
     uniformly (recorded per call as max_tokens_sent).

Resume rule: interrupted launches resume at SEED granularity; provider-failure
sessions are terminal and never retried.
"""
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[0]
sys.path.insert(0, str(ROOT))

REG = json.loads((HERE / "_REGISTRATION.json").read_text())
FROZEN = ROOT / "run_info_contract_2x2_aesgcm.py"
got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
if got != REG["runner"]:
    raise SystemExit(f"FROZEN RUNNER HASH MISMATCH: {got} != {REG['runner']}")

ADAPTER = ROOT / "provider_adapter_agentrouter_p023.py"
adapter_sha = hashlib.sha256(ADAPTER.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)
if not hasattr(injected, "ClaudeProvider") or not hasattr(injected, "ProviderFailure"):
    raise SystemExit("injected adapter missing ClaudeProvider/ProviderFailure")

import run_info_contract_2x2_aesgcm as base  # noqa: E402

if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did NOT bind the injected provider — aborting")
if base.ClaudeProvider.__module__ != "provider_adapter":
    raise SystemExit(f"unexpected provider module binding: {base.ClaudeProvider.__module__}")

base.OUT = HERE
base.PROTOCOL = "P014-INFO-CONTRACT-2X2-AESGCM-NONCE-REUSE-v1"
for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (HERE / sub).mkdir(parents=True, exist_ok=True)

SEEDS = tuple(int(v) for v in os.environ.get(
    "ACTS_SEEDS", ",".join(str(s) for s in range(401, 417))).split(",") if v.strip())
base.SEEDS = SEEDS
base.ROTATIONS = {i: base.ROTATIONS[i % 4] for i in range(max(len(SEEDS), 4))}

provider_probe = injected.ClaudeProvider()  # resolves endpoint/model/key; no call
launch = {
    "protocol": base.PROTOCOL,
    "namespace": HERE.name,
    "runner_sha256": got,
    "adapter_sha256": adapter_sha,
    "model_label": provider_probe.model,
    "endpoint_host": provider_probe.endpoint.split("//")[-1].split("/")[0],
    "seeds": list(SEEDS),
    "sessions_registered": 4 * len(SEEDS),
    "token_floor": getattr(injected, "LABEL2_TOKEN_FLOOR", None),
    "user_agent": getattr(injected, "LABEL2_UA", None),
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
